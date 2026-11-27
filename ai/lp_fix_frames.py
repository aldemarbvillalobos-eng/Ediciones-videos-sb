"""Regenera fotogramas concretos de una reactuación (p. ej. los que fallaron en la detección), con la misma referencia
de expresión. Uso: lp_fix_frames.py <retrato.png> <video_conductor> <lp_dir> <frame_i> [<frame_i> ...]"""
import sys, os, json, importlib.util
import numpy as np, cv2, av, torch
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("LP_SCALE", "2.0"); os.environ.setdefault("LP_VY", "-0.08")
portrait, drv_path, lp_dir = sys.argv[1], sys.argv[2], sys.argv[3]; todo = [int(x) for x in sys.argv[4:]]
# Reutiliza las piezas de lp_reenact sin ejecutar su flujo principal
src_code = open(os.path.join(HERE, "lp_reenact.py")).read().split("# --- Fuente: retrato")[0]
sys.argv = [sys.argv[0], portrait, drv_path, "0", "0", lp_dir]; g = {"__file__": os.path.join(HERE, "lp_reenact.py")}; exec(src_code, g)
lp, crop_image, CROP, landmarker, pts5_from, get_rotation_matrix = g["lp"], g["crop_image"], g["CROP"], g["landmarker"], g["pts5_from"], g["get_rotation_matrix"]
import mediapipe as mp
meta = json.load(open(f"{lp_dir}/meta.json")); fps = meta["fps"]
srcimg = cv2.cvtColor(cv2.imread(portrait), cv2.COLOR_BGR2RGB); lm = landmarker(False)
s5, _ = pts5_from(lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=srcimg)).face_landmarks[0], srcimg.shape[1], srcimg.shape[0])
sc = crop_image(srcimg, s5, **CROP)
with torch.no_grad():
    I_s = lp.prepare_source(cv2.resize(sc["img_crop"], (256, 256))); xs_info = lp.get_kp_info(I_s); f_s = lp.extract_feature_3d(I_s); x_s = lp.transform_keypoint(xs_info)
    ref = cv2.cvtColor(cv2.imread(f"{lp_dir}/drv/drv_{meta['ref']:05d}.png"), cv2.COLOR_BGR2RGB)
    exp_ref = lp.get_kp_info(lp.prepare_source(cv2.resize(ref, (256, 256))))["exp"]
n_next = max(f.get("n", -1) for f in meta["frames"]) + 1
c = av.open(drv_path); st = c.streams.video[0]
for i, fr in enumerate(c.decode(st)):
    if i > max(todo): break
    if i not in todo: continue
    img = fr.to_ndarray(format="rgb24"); h, w = img.shape[:2]
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=img))
    if not r.face_landmarks: print("sin cara en", i); continue
    p5, P = pts5_from(r.face_landmarks[0], w, h); dc = crop_image(img, p5, **CROP)
    with torch.no_grad():
        d = lp.get_kp_info(lp.prepare_source(cv2.resize(dc["img_crop"], (256, 256))))
        R_d = get_rotation_matrix(d["pitch"], d["yaw"], d["roll"]); exp_new = xs_info["exp"] + (d["exp"] - exp_ref)
        kp_new = d["scale"] * (xs_info["kp"] @ R_d + exp_new) + d["t"]
        out = lp.parse_output(lp.warp_decode(f_s, x_s, kp_new)["out"])[0]
    cv2.imwrite(f"{lp_dir}/gen/gen_{n_next:05d}.png", cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    cv2.imwrite(f"{lp_dir}/drv/drv_{n_next:05d}.png", cv2.cvtColor(dc["img_crop"], cv2.COLOR_RGB2BGR))
    for f in meta["frames"]:
        if f["i"] == i:
            f.update({"n": n_next, "ok": True, "cut": True, "M_c2o": dc["M_c2o"].tolist(), "chin": P[152].tolist(), "top": P[10].tolist(),
                      "face_h": float(np.linalg.norm(P[10] - P[152])), "mouth": 0.0})
    print("regenerado", i, "→ gen", n_next); n_next += 1
json.dump(meta, open(f"{lp_dir}/meta.json", "w"))
