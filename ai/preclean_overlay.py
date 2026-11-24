"""Elimina un gráfico incrustado (p. ej. rótulo de nombre) ANTES de segmentar, sin tocar a la persona.
- Placa de fondo limpia: mediana temporal de la zona en un tramo sin gráfico.
- Píxeles gráficos sobre el fondo → placa limpia.  Píxeles gráficos sobre la persona (piel) → inpainting OpenCV.
Genera una copia de trabajo del video (0..fin) con la zona limpia en la ventana indicada; el original no se toca.
Uso: preclean_overlay.py <config.json>  (src, out, end, rect, win:[t0,t1], plate:[t0,t1])"""
import sys, json, subprocess, av, numpy as np, cv2
cfg = json.load(open(sys.argv[1])); x0, y0, x1, y1 = cfg["rect"]; w0, w1 = cfg["win"]; p0, p1 = cfg["plate"]
c = av.open(cfg["src"]); s = c.streams.video[0]; fps = float(s.average_rate)
# Placa: mediana temporal SOLO de píxeles de fondo (alfa RVM < 0,05) y fuera de las cajas de subtítulos
subs = {int(k): v for k, v in json.load(open(cfg["subs"])).items()} if cfg.get("subs") else {}
stack = []
for fr in c.decode(s):
    t = float(fr.pts * s.time_base); idx = round(t * fps)
    if t > p1: break
    if not (p0 <= t <= p1 and idx % 3 == 0): continue
    reg = fr.to_ndarray(format="rgb24")[y0:y1, x0:x1].astype(np.float32)
    ok = np.ones(reg.shape[:2], bool)
    if cfg.get("alpha"):
        a = cv2.imread(f"{cfg['alpha']}/alpha_{idx:05d}.png", 0)
        if a is not None: ok &= cv2.dilate(a, np.ones((15, 15), np.uint8))[y0:y1, x0:x1] < 13
    for bx0, by0, bx1, by1, *_ in subs.get(idx, []): ok[max(0, by0 - 14 - y0):max(0, by1 + 14 - y0), max(0, bx0 - 18 - x0):max(0, bx1 + 18 - x0)] = False
    reg[~ok] = np.nan; stack.append(reg)
plate = np.nanmedian(np.stack(stack), 0)
holes = np.isnan(plate[..., 0])
if holes.any():  # huecos nunca vistos como fondo: interpolar
    pl = np.nan_to_num(plate).astype(np.uint8); plate = cv2.inpaint(pl, holes.astype(np.uint8), 9, cv2.INPAINT_TELEA)
plate = plate.astype(np.uint8); c.close(); print("placa: huecos", int(holes.sum()))
c = av.open(cfg["src"]); s = c.streams.video[0]; W, H = s.width, s.height
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-c:v", "libx264", "-qp", "0", "-preset", "veryfast", "-pix_fmt", "yuv444p", cfg["out"]], stdin=subprocess.PIPE)
n = 0
for fr in c.decode(s):
    t = float(fr.pts * s.time_base)
    if t > cfg["end"]: break
    img = fr.to_ndarray(format="rgb24")
    if w0 <= t <= w1:
        sub = img[y0:y1, x0:x1].astype(np.float32) / 255; L = sub.mean(2); sat = sub.max(2) - sub.min(2)
        white = (L > 0.42) & (sat < 0.28)
        blue = (sub[..., 2] > sub[..., 0] + 0.05) & (sub[..., 2] > sub[..., 1] + 0.03) & (sub[..., 2] > 0.14)
        skin = (sub[..., 0] > sub[..., 2] + 0.06) & (sub[..., 0] > 0.20)
        G = cv2.dilate((white | blue).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        # ¿fondo o persona? diferencia con la placa limpia fuera de los píxeles gráficos
        diff = np.abs(sub - plate.astype(np.float32) / 255).mean(2)
        bgish = cv2.erode(((diff < 0.06) | G).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        person = cv2.dilate((skin | (~bgish & ~G)).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        out = img[y0:y1, x0:x1].copy()
        on_bg = G & ~person; on_p = G & person
        out[on_bg] = plate[on_bg]
        if on_p.any():
            # relleno por convolución normalizada desde los píxeles de persona NO gráficos (piel / manga), multiescala
            valid = (~G & person).astype(np.float32); src = out.astype(np.float32); fill = np.zeros_like(src); done = np.zeros(valid.shape, bool)
            for sg in (3, 6, 12, 24):
                num = cv2.GaussianBlur(src * valid[..., None], (0, 0), sg); den = cv2.GaussianBlur(valid, (0, 0), sg)
                ok = (den > 0.15) & ~done; fill[ok] = num[ok] / den[ok][:, None]; done |= ok
            fill[~done] = src[~done]
            out[on_p] = np.clip(fill[on_p], 0, 255).astype(np.uint8)
        img = img.copy(); img[y0:y1, x0:x1] = out
    enc.stdin.write(img.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("limpio", n, "frames →", cfg["out"])
