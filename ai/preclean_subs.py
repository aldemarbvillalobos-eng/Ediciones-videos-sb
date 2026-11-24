"""Copia de ANÁLISIS (solo para que el modelo de segmentación no confunda los subtítulos con la persona):
deshace el oscurecimiento de las cajas de subtítulos y rellena las letras por inpainting.
Los píxeles finales del video siguen saliendo del original (subtítulos incluidos).
Uso: preclean_subs.py <entrada> <subs_events.json> <t0> <t1> <salida> [opacidad_caja] [pad x0,y0,x1,y1]"""
import sys, json, subprocess, av, numpy as np, cv2
src, evp, t0, t1, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
k = float(sys.argv[6]) if len(sys.argv) > 6 else 0.18; pad = [int(v) for v in (sys.argv[7] if len(sys.argv) > 7 else "14,10,14,10").split(",")]
ev = {int(kk): v for kk, v in json.load(open(evp)).items()}
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate); W, H = s.width, s.height
enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-c:v", "libx264", "-qp", "0", "-preset", "veryfast", "-pix_fmt", "yuv444p", out], stdin=subprocess.PIPE)
for fr in c.decode(s):
    t = float(fr.pts * s.time_base); idx = round(t * fps)
    if t > t1 + 0.1: break
    img = fr.to_ndarray(format="rgb24")
    boxes = ev.get(idx, []) if t >= t0 - 1e-3 else []
    if boxes:
        f = img.astype(np.float32); mask = np.zeros((H, W), np.uint8)
        for x0, y0, x1, y1, *_ in boxes:
            X0, Y0, X1, Y1 = max(0, x0 - pad[0]), max(0, y0 - pad[1]), min(W, x1 + pad[2]), min(H, y1 + pad[3])
            reg = f[Y0:Y1, X0:X1]; L = reg.mean(2); sat = reg.max(2) - reg.min(2)
            Lb = cv2.blur(cv2.erode(L, np.ones((9, 9), np.uint8)), (9, 9))
            mask[Y0:Y1, X0:X1] |= (((L - Lb) > 40) & (sat < 60)).astype(np.uint8)
            f[Y0:Y1, X0:X1] = np.clip(reg / (1 - k), 0, 255)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
        img = cv2.inpaint(f.astype(np.uint8), mask, 5, cv2.INPAINT_TELEA)
    enc.stdin.write(np.ascontiguousarray(img).tobytes())
enc.stdin.close(); enc.wait(); print("copia de análisis →", out)
