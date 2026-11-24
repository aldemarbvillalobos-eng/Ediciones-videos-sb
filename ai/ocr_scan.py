"""OCR por segundo (Tesseract spa) de zonas: título superior, rótulo inferior izquierdo y subtítulos.
Uso: .venv-ai/bin/python ai/ocr_scan.py <video> <salida.json> [paso_s]"""
import sys, json, av, numpy as np, pytesseract, cv2
src, out = sys.argv[1], sys.argv[2]; step = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
c = av.open(src); s = c.streams.video[0]; res = []; nxt = 0.0
ZONES = {"titulo": (0, 0, 1920, 430), "rotulo": (60, 880, 700, 1080), "subs": (300, 880, 1620, 1060)}
for fr in c.decode(s):
    t = float(fr.pts * s.time_base)
    if t + 1e-6 < nxt: continue
    nxt += step; img = fr.to_ndarray(format="rgb24"); row = {"t": round(t, 2), "yavg": float(img.mean())}
    for k, (x0, y0, x1, y1) in ZONES.items():
        g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY)
        g = cv2.threshold(g, 170, 255, cv2.THRESH_BINARY_INV)[1]
        row[k] = " ".join(pytesseract.image_to_string(g, lang="spa+eng", config="--psm 6").split())
    res.append(row); print(row["t"], "|", row["titulo"][:50], "|", row["rotulo"][:40], "|", row["subs"][:70], flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
