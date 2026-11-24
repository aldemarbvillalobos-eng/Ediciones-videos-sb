"""Composición: persona original (alpha RVM) sobre el fondo de estudio, con
 - descontaminación de bordes (quita el azul del fondo original en cabello y contornos) y envoltura de luz,
 - eliminación del rótulo original (solo píxeles gráficos dentro de su zona y ventana de tiempo),
 - protección de subtítulos: la caja semitransparente se reconstruye sobre el nuevo fondo y el texto original
   se repinta con su alfa (no se reescribe ni se retraduce nada),
 - grano de película igual al original.
La persona (rostro, cabello, manos, ropa) se toma siempre de los píxeles ORIGINALES; no se regenera nada.
Uso: composite_bg.py <config.json>"""
import sys, json, os, subprocess, av, numpy as np, cv2
cfg = json.load(open(sys.argv[1])); src = cfg["src"]; t0, t1 = cfg["t0"], cfg["t1"]
bg_default = np.load(cfg["bg"]).astype(np.float32); H, W = bg_default.shape[:2]
bg_ranges = [(int(a), int(b), np.load(p).astype(np.float32)) for a, b, p in cfg.get("bgRanges", [])]  # [frame_ini, frame_fin, fondo.npy] por plano
subs = {int(k): v for k, v in json.load(open(cfg["subs"])).items()} if cfg.get("subs") else {}
subs_keys = np.array(sorted(subs)) if subs else np.array([])
LT = cfg.get("lowerThird")  # {"t0","t1","rect":[x0,y0,x1,y1]}
K_BOX = cfg.get("boxOpacity", 0.45); PAD = cfg.get("boxPad", [14, 10, 14, 12])
os.makedirs(os.path.dirname(cfg["out"]), exist_ok=True)
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate)
c.seek(int(max(0, t0 - 1) / s.time_base), stream=s, backward=True)
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-ss", str(t0), "-t", str(t1 - t0), "-i", cfg.get("audioSrc", src), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "copy", "-shortest", cfg["out"]], stdin=subprocess.PIPE)
rng = np.random.default_rng(3); n = 0; dbg = cfg.get("debugFrames", [])
def nearest_subs(idx):
    if not len(subs_keys): return []
    j = np.searchsorted(subs_keys, idx); cands = [subs_keys[k] for k in (j - 1, j) if 0 <= k < len(subs_keys)]
    return subs[min(cands, key=lambda k: abs(k - idx))]
for fr in c.decode(s):
    t = float(fr.pts * s.time_base); idx = round(t * fps)
    if t < t0 - 1e-3: continue
    if t > t1 + 1e-3: break
    I = fr.to_ndarray(format="rgb24").astype(np.float32) / 255
    bg = next((b_ for a_, z_, b_ in bg_ranges if a_ <= idx <= z_), bg_default)
    a = cv2.imread(os.path.join(cfg["alpha"], f"alpha_{idx:05d}.png"), 0).astype(np.float32) / 255
    L = I.mean(2); sat = I.max(2) - I.min(2)
    # 1) Rótulo original: sus píxeles gráficos (texto blanco, líneas azules y el contorno conocido de la caja)
    #    - sobre el FONDO → transparentes (los cubre el fondo nuevo)
    #    - sobre la PERSONA (p. ej. líneas que cruzan los dedos) → se reconstruyen con inpainting desde la piel vecina
    if LT and LT["t0"] <= t <= LT["t1"]:
        x0, y0, x1, y1 = LT["rect"]; sub = I[y0:y1, x0:x1]
        g = ((L[y0:y1, x0:x1] > 0.45) & (sat[y0:y1, x0:x1] < 0.28)) | ((sub[..., 2] > sub[..., 0] + 0.05) & (sub[..., 2] > sub[..., 1] + 0.03) & (sub[..., 2] > 0.16))
        lines = np.zeros_like(g)
        for lx0, ly0, lx1, ly1 in LT.get("lines", []): lines[ly0 - y0:ly1 - y0, lx0 - x0:lx1 - x0] = True
        skin = (sub[..., 0] > sub[..., 2] + 0.06) & (sub[..., 0] > 0.22)
        gp = os.path.join(cfg.get("gate", ""), f"gate_{idx:05d}.png")
        gate = cv2.imread(gp, 0)[y0:y1, x0:x1] > 127 if (cfg.get("gate") and os.path.exists(gp)) else (a[y0:y1, x0:x1] > 0.5)
        person = cv2.dilate((gate | skin).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        G = cv2.dilate((g | lines).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        on_p = G & person  # gráfico encima de la persona
        if on_p.any():
            fixed = cv2.inpaint((sub * 255).astype(np.uint8), G.astype(np.uint8), 4, cv2.INPAINT_TELEA).astype(np.float32) / 255
            I[y0:y1, x0:x1][on_p] = fixed[on_p]; L = I.mean(2); sat = I.max(2) - I.min(2)
        a[y0:y1, x0:x1][G & ~on_p] = 0
        if cfg.get("gate") and os.path.exists(gp):  # guía SAM2 suavizada: solo la persona dentro de la zona del rótulo
            gm = cv2.GaussianBlur(cv2.dilate(cv2.imread(gp, 0), np.ones((15, 15), np.uint8)).astype(np.float32) / 255, (0, 0), 3)
            hh, ww = y1 - y0, x1 - x0; fy = np.minimum(np.arange(hh), np.arange(hh)[::-1]) / 40.0; fx = np.minimum(np.arange(ww), np.arange(ww)[::-1]) / 60.0
            infl = np.clip(np.minimum(fy[:, None], fx[None, :]), 0, 1)
            sub2 = I[y0:y1, x0:x1]; navy = (sub2[..., 2] > sub2[..., 1] + 0.012) & (sub2[..., 2] > sub2[..., 0])  # solo píxeles con color de fondo
            infl = infl * navy
            a[y0:y1, x0:x1] *= 1 - infl * (1 - gm[y0:y1, x0:x1])
    # 2) Subtítulos: cajas de línea y alfa del texto
    raw = [b for d_ in (-2, -1, 0, 1, 2) for b in nearest_subs(idx + d_)]
    uniq = {tuple(b[:4]) for b in raw}
    boxes = [[max(0, b[0] - PAD[0]), max(0, b[1] - PAD[1]), min(W, b[2] + PAD[2]), min(H, b[3] + PAD[3])] for b in uniq]
    box_m = np.zeros((H, W), np.float32); ta = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1 in boxes:
        box_m[y0:y1, x0:x1] = 1
        Lb = cv2.blur(cv2.erode(L[y0:y1, x0:x1], np.ones((9, 9), np.uint8)), (9, 9))
        tt = np.clip((L[y0:y1, x0:x1] - Lb) / np.maximum(1 - Lb, 0.2), 0, 1) * (sat[y0:y1, x0:x1] < 0.25)
        ta[y0:y1, x0:x1] = np.clip((tt - 0.10) / 0.75, 0, 1)
        # prior de cuerpo bajo la caja: alfa de las filas justo encima (columna a columna)
        prior = a[max(0, y0 - 14):max(1, y0 - 4), x0:x1].max(0, initial=0)
        prior = cv2.dilate(prior[None], np.ones((1, 15), np.uint8))[0]
        txt = cv2.dilate((ta[y0:y1, x0:x1] > 0.08).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        aa = a[y0:y1, x0:x1]; aa[txt & (prior[None] < 0.5)] = 0
    # 3) Fondo original estimado (para descontaminar bordes)
    wgt = (a < 0.02).astype(np.float32) * (1 - box_m)
    Bo = cv2.GaussianBlur(I * wgt[..., None], (0, 0), 21) / (cv2.GaussianBlur(wgt, (0, 0), 21)[..., None] + 1e-4)
    a3 = a[..., None]; edge = (a > 0.02) & (a < 0.98)
    fg = I.copy(); fg[edge] = np.clip((I[edge] - (1 - a3[edge]) * Bo[edge]) / np.maximum(a3[edge], 0.08), 0, 1)
    # 4) Fondo nuevo (+ caja de subtítulo reconstruida) y grano
    B = bg * (1 - K_BOX * box_m[..., None]) + rng.normal(0, 1.3 / 255, (H, W, 3)).astype(np.float32)
    C = fg * a3 + B * (1 - a3)
    # 5) Envoltura de luz sutil en los bordes para integrar a la persona en el set
    wrap = cv2.GaussianBlur(B * (1 - a3), (0, 0), 8) * (a3 * (1 - cv2.GaussianBlur(a, (0, 0), 8)[..., None]))
    C = C + 0.35 * wrap
    # 6) Texto original repintado sobre el fondo (sobre el cuerpo ya está en los píxeles originales)
    tb = (ta * (1 - a))[..., None]; C = C * (1 - tb) + tb
    out = (np.clip(C, 0, 1) * 255 + 0.5).astype(np.uint8)
    enc.stdin.write(out.tobytes()); n += 1
    if idx in dbg:
        cv2.imwrite(os.path.join(os.path.dirname(cfg["out"]), f"debug_{idx:05d}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(os.path.dirname(cfg["out"]), f"debug_{idx:05d}_alpha.png"), (a * 255).astype(np.uint8))
    if n % 60 == 0: print("frames", n, flush=True)
enc.stdin.close(); enc.wait(); print("listo", n, "frames →", cfg["out"])
