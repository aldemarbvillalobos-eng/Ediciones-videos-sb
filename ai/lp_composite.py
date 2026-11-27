"""Sustitución de la cabeza de la presentadora por la presentadora virtual animada (salida de lp_reenact.py).
- Quita la cabeza original usando el fondo de estudio exacto y la alfa RVM de la presentadora.
- Coloca la cabeza nueva (recorte 512 de LivePortrait) con su propia alfa (RVM sobre los recortes generados).
- Funde el cuello con el cuerpo original en una franja bajo el mentón e iguala el tono de piel del cuello.
- Subtítulos, cuerpo, manos y fondo no se tocan. Audio: el del máster (original).
Uso: lp_composite.py <config.json>
config: master, t0, t1, src_offset (seg. del original que corresponden al 0 del máster), lp_dir, gen_alpha_dir,
        alpha_dir (alfa presentadora, índice ordinal del original), bg, bgRanges, out"""
import sys, os, json, subprocess
import numpy as np, cv2, av

cfg = json.load(open(sys.argv[1])); meta = json.load(open(os.path.join(cfg["lp_dir"], "meta.json")))
fps = meta["fps"]; W, H = 1920, 1080
bg0 = np.load(cfg["bg"]).astype(np.float32)
bgr = [(a, b, np.load(p).astype(np.float32)) for a, b, p in cfg.get("bgRanges", [])]
info = {f["i"]: f for f in meta["frames"]}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(5)

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

c = av.open(cfg["master"]); st = c.streams.video[0]
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-ss", str(cfg["t0"]), "-t", str(cfg["t1"] - cfg["t0"] + 1 / fps), "-i", cfg["master"], "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-c:a", "copy", "-shortest", cfg["out"]], stdin=subprocess.PIPE)
crop_feather = np.zeros((512, 512), np.float32); cv2.rectangle(crop_feather, (12, 12), (499, 499), 1.0, -1)
crop_feather = cv2.GaussianBlur(crop_feather, (0, 0), 8)
gain_prev = None; dbg = set(cfg.get("debugFrames", [])); nout = 0
for i, fr in enumerate(c.decode(st)):
    t = i / fps
    if t < cfg["t0"] - 1e-6: continue
    if t > cfg["t1"] + 1e-6: break
    F = fr.to_ndarray(format="rgb24").astype(np.float32) / 255
    f = info.get(i)
    if f and f.get("ok"):
        src_idx = i + int(round(cfg["src_offset"] * fps))
        A = cv2.imread(os.path.join(cfg["alpha_dir"], f"alpha_{src_idx:05d}.png"), 0).astype(np.float32) / 255
        bg = next((b for a_, z_, b in bgr if a_ <= src_idx <= z_), bg0)
        yc, fh = f["chin"][1], f["face_h"]
        # 1) quitar la cabeza original (incluido el pelo) → fondo de estudio exacto
        cx = f["chin"][0]
        col_old = 1 - smoothstep(0.24 * fh, 0.32 * fh, np.abs(xx - cx))   # columna del cuello original (no hombros)
        below = smoothstep(yc - 0.02 * fh, yc + 0.08 * fh, yy)            # 0 por encima del mentón, 1 por debajo
        Hm = A * ((1 - below) + below * col_old * (1 - smoothstep(yc + 0.10 * fh, yc + 0.22 * fh, yy)))
        F1 = F * (1 - Hm[..., None]) + (bg + rng.normal(0, 1.3 / 255, bg.shape).astype(np.float32)) * Hm[..., None]
        # 2) cabeza nueva al fotograma
        n = f["n"]; G = cv2.cvtColor(cv2.imread(os.path.join(cfg["lp_dir"], "gen", f"gen_{n:05d}.png")), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        ag = cv2.imread(os.path.join(cfg["gen_alpha_dir"], f"alpha_{n:05d}.png"), 0).astype(np.float32) / 255
        # descontaminación del borde (cabello): quita el color del fondo del retrato generado
        wb = (ag < 0.03).astype(np.float32)
        Bo = cv2.GaussianBlur(G * wb[..., None], (0, 0), 15) / (cv2.GaussianBlur(wb, (0, 0), 15)[..., None] + 1e-4)
        e = (ag > 0.03) & (ag < 0.97); a3 = ag[..., None]
        G[e] = np.clip((G[e] - (1 - a3[e]) * Bo[e]) / np.maximum(a3[e], 0.15), 0, 1)
        ag = ag * crop_feather
        M = np.array(f["M_c2o"], np.float32)[:2]
        Gw = cv2.warpAffine(G, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        Aw = cv2.warpAffine(ag, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        # 3) cuello: la cabeza nueva llega algo más abajo que el corte de la original y se funde con el cuello real
        col_new = 1 - smoothstep(0.30 * fh, 0.42 * fh, np.abs(xx - cx))   # solo el cuello nuevo bajo el mentón
        N = Aw * ((1 - below) + below * col_new * (1 - smoothstep(yc + 0.26 * fh, yc + 0.46 * fh, yy)))
        # igualar tono de piel del cuello nuevo al cuello real (franja bajo el mentón), suavizado en el tiempo
        x0, x1 = int(f["chin"][0] - 0.18 * fh), int(f["chin"][0] + 0.18 * fh)
        b0, b1 = int(yc + 0.12 * fh), int(yc + 0.3 * fh)
        old = F[b0:b1, x0:x1][A[b0:b1, x0:x1] > 0.95]; new = Gw[b0:b1, x0:x1][Aw[b0:b1, x0:x1] > 0.95]
        if len(old) > 50 and len(new) > 50:
            gain = np.clip(np.median(old, 0) / np.maximum(np.median(new, 0), 1e-3), 0.75, 1.3)
            gain_prev = gain if gain_prev is None else 0.9 * gain_prev + 0.1 * gain
        if gain_prev is not None:
            k = cfg.get("skinMatch", 0.6); w_neck = smoothstep(yc - 0.1 * fh, yc + 0.25 * fh, yy)[..., None]
            Gw = Gw * (1 + (gain_prev - 1) * k * (0.35 + 0.65 * w_neck))  # más ajuste en el cuello, menos en la cara
        F = F1 * (1 - N[..., None]) + Gw * N[..., None]
        if i in dbg:
            cv2.imwrite(os.path.join(os.path.dirname(cfg["out"]), f"ia_debug_{i:05d}.png"), cv2.cvtColor((np.clip(F, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    enc.stdin.write((np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()); nout += 1
    if nout % 60 == 0: print("fotogramas", nout, flush=True)
enc.stdin.close(); enc.wait(); print("listo", nout, "→", cfg["out"])
