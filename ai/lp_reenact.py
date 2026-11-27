"""Reactuación facial: anima el retrato de la presentadora virtual con los movimientos, gestos y labios de la
actuación ORIGINAL (LivePortrait, MIT). La detección facial usa MediaPipe Face Landmarker (Apache-2.0) en lugar de
InsightFace (no comercial).

Uso: lp_reenact.py <retrato.png> <video_conductor> <t0> <t1> <salida_dir>
Salida (por fotograma n del tramo): gen/gen_%05d.png (cabeza nueva 512×512), drv/drv_%05d.png (recorte del conductor)
y meta.json (matriz recorte→fotograma, mentón y altura de cara en coordenadas del fotograma, cortes de plano)."""
import sys, os, json, time
import numpy as np, cv2, av, torch
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.join(HERE, "vendor", "LivePortrait")
sys.path.insert(0, LP)
from src.config.inference_config import InferenceConfig  # noqa: E402
from src.live_portrait_wrapper import LivePortraitWrapper  # noqa: E402
import src.utils.crop as lpcrop  # noqa: E402
from src.utils.crop import crop_image  # noqa: E402

# Soporte de la malla completa de MediaPipe (478 puntos) en el recorte de LivePortrait:
# rotación por centro de ojos y centro de boca; tamaño por el contorno completo de la cara.
_orig_pt2 = lpcrop.parse_pt2_from_pt_x
def _pt2_478(pts, use_lip=True):
    if pts.shape[0] == 478:
        return np.stack([(pts[468] + pts[473]) / 2, (pts[61] + pts[291]) / 2 if use_lip else pts[473]], axis=0)
    return _orig_pt2(pts, use_lip=use_lip)
lpcrop.parse_pt2_from_pt_x = _pt2_478
from src.utils.camera import get_rotation_matrix  # noqa: E402

portrait, drv_path, t0, t1, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
os.makedirs(f"{out}/gen", exist_ok=True); os.makedirs(f"{out}/drv", exist_ok=True)
torch.set_num_threads(4)
W = os.path.join(HERE, "models", "liveportrait", "liveportrait")
cfg = InferenceConfig(checkpoint_F=f"{W}/base_models/appearance_feature_extractor.pth", checkpoint_M=f"{W}/base_models/motion_extractor.pth",
                      checkpoint_G=f"{W}/base_models/spade_generator.pth", checkpoint_W=f"{W}/base_models/warping_module.pth",
                      checkpoint_S=f"{W}/retargeting_models/stitching_retargeting_module.pth", flag_force_cpu=True, flag_use_half_precision=False)
lp = LivePortraitWrapper(inference_cfg=cfg)

def landmarker(video_mode):
    return vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(HERE, "models", "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO if video_mode else vision.RunningMode.IMAGE, num_faces=1))

def pts5_from(lm, w, h):
    P = np.array([[p.x * w, p.y * h] for p in lm], np.float32)
    # ojos (centro del iris), punta de la nariz, comisuras de la boca
    return P, P  # malla completa (478)

CROP = dict(dsize=512, scale=float(os.environ.get("LP_SCALE", "2.6")), vx_ratio=0.0, vy_ratio=float(os.environ.get("LP_VY", "-0.06")), flag_do_rot=True)

# --- Fuente: retrato de la presentadora virtual
src = cv2.cvtColor(cv2.imread(portrait), cv2.COLOR_BGR2RGB)
r = landmarker(False).detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=src))
s5, _ = pts5_from(r.face_landmarks[0], src.shape[1], src.shape[0])
sc = crop_image(src, s5, **CROP)
cv2.imwrite(f"{out}/source_crop.png", cv2.cvtColor(sc["img_crop"], cv2.COLOR_RGB2BGR))
with torch.no_grad():
    I_s = lp.prepare_source(cv2.resize(sc["img_crop"], (256, 256)))
    x_s_info = lp.get_kp_info(I_s); f_s = lp.extract_feature_3d(I_s); x_s = lp.transform_keypoint(x_s_info)
    x_c_s = x_s_info["kp"]

# --- Conductor: actuación original (fotogramas del máster de estudio)
lmk_v = landmarker(True); lmk_i = landmarker(False)
c = av.open(drv_path); st = c.streams.video[0]; fps = float(st.average_rate)
frames_info = []; prev5 = None; n = 0; tic = time.time()
drv_infos = []
for i, fr in enumerate(c.decode(st)):
    t = i / fps
    if t < t0 - 1e-6: continue
    if t > t1 + 1e-6: break
    img = fr.to_ndarray(format="rgb24"); h, w = img.shape[:2]
    res = lmk_v.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=img), int(round(t * 1000)))
    if not res.face_landmarks:  # el seguimiento pierde la cara (p. ej. primer fotograma tras un corte): detección por imagen
        res = lmk_i.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=img))
    if not res.face_landmarks:
        frames_info.append({"i": i, "ok": False}); continue
    p5, P = pts5_from(res.face_landmarks[0], w, h)
    cut = prev5 is not None and np.abs(p5 - prev5).mean() > 25  # cambio de plano: no suavizar entre planos
    p5s = p5 if (prev5 is None or cut) else 0.5 * p5 + 0.5 * prev5   # suavizado temporal leve del recorte
    prev5 = p5s
    dc = crop_image(img, p5s, **CROP)
    with torch.no_grad():
        I_d = lp.prepare_source(cv2.resize(dc["img_crop"], (256, 256)))
        info = lp.get_kp_info(I_d)
    mouth = float(np.linalg.norm(P[13] - P[14]) / (np.linalg.norm(P[10] - P[152]) + 1e-6))
    drv_infos.append({k: v.clone() for k, v in info.items() if torch.is_tensor(v)})
    cv2.imwrite(f"{out}/drv/drv_{n:05d}.png", cv2.cvtColor(dc["img_crop"], cv2.COLOR_RGB2BGR))
    frames_info.append({"i": i, "n": n, "ok": True, "cut": bool(cut), "M_c2o": dc["M_c2o"].tolist(), "mouth": mouth,
                        "chin": P[152].tolist(), "top": P[10].tolist(), "face_h": float(np.linalg.norm(P[10] - P[152]))})
    n += 1
print("conductor:", n, "fotogramas", round(time.time() - tic, 1), "s", flush=True)

# Referencia de expresión: el fotograma con la boca más cerrada (la expresión del retrato es neutra, boca cerrada)
oks = [f for f in frames_info if f["ok"]]
ref = min(oks, key=lambda f: f["mouth"])["n"]; exp_ref = drv_infos[ref]["exp"]
if os.environ.get("LP_REF_DRV"):  # referencia fija (p. ej. la de la muestra aprobada) para mantener idéntica la interpretación
    with torch.no_grad():
        _r = cv2.cvtColor(cv2.imread(os.environ["LP_REF_DRV"]), cv2.COLOR_BGR2RGB)
        exp_ref = lp.get_kp_info(lp.prepare_source(cv2.resize(_r, (256, 256))))["exp"]
print("referencia de expresión: fotograma", ref, flush=True)

tic = time.time()
with torch.no_grad():
    for f in oks:
        d = drv_infos[f["n"]]
        R_d = get_rotation_matrix(d["pitch"], d["yaw"], d["roll"])
        delta = d["exp"] - exp_ref
        # amplificación SOLO de los puntos de los labios (LivePortrait: 6, 12, 14, 17, 19, 20) para no amortiguar la vocalización
        lip_gain = float(os.environ.get("LP_LIP_GAIN", "1.0"))
        if lip_gain != 1.0:
            delta = delta.clone(); delta[:, [6, 12, 14, 17, 19, 20], :] *= lip_gain
        exp_new = x_s_info["exp"] + delta          # expresión relativa (conserva la identidad nueva)
        lip_abs = float(os.environ.get("LP_LIP_ABS", "0"))   # 0–1: forma absoluta de los labios del conductor (fruncido o/u)
        if lip_abs > 0:
            L = [6, 12, 14, 17, 19, 20]
            exp_new = exp_new.clone(); exp_new[:, L, :] = (1 - lip_abs) * exp_new[:, L, :] + lip_abs * d["exp"][:, L, :]
        kp_new = d["scale"] * (x_c_s @ R_d + exp_new) + d["t"]   # pose, escala y posición absolutas del conductor
        kp_new[..., 2] = (d["scale"] * (x_c_s @ R_d + exp_new))[..., 2]
        out_t = lp.warp_decode(f_s, x_s, kp_new)["out"]
        g = lp.parse_output(out_t)[0]
        cv2.imwrite(f"{out}/gen/gen_{f['n']:05d}.png", cv2.cvtColor(g, cv2.COLOR_RGB2BGR))
        if f["n"] % 50 == 0: print("generado", f["n"], round(time.time() - tic, 1), "s", flush=True)
json.dump({"fps": fps, "t0": t0, "t1": t1, "ref": ref, "frames": frames_info}, open(f"{out}/meta.json", "w"))
print("listo", len(oks), "fotogramas →", out)
