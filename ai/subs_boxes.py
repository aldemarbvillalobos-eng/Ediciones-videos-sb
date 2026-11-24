"""Detecta las cajas de los subtítulos incrustados por OCR (Tesseract) cada N frames.
Uso: subs_boxes.py <video> <t0> <t1> <salida.json> [cada_n_frames]
Salida: {frame_idx: [[x0,y0,x1,y1,texto], ...]} con índice = frame del original."""
import sys, json, av, numpy as np, cv2, pytesseract
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]; every = int(sys.argv[5]) if len(sys.argv) > 5 else 3
Y0 = 850
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate); c.seek(int(max(0, t0 - 1) / s.time_base), stream=s, backward=True)
res = {}
for fr in c.decode(s):
    t = float(fr.pts * s.time_base); idx = round(t * fps)
    if t < t0 - 1e-3 or idx % every: continue
    if t > t1: break
    img = fr.to_ndarray(format="rgb24")[Y0:]; L = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    sat = img.max(2).astype(int) - img.min(2)
    m = ((L > 185) & (sat < 45)).astype(np.uint8) * 255
    d = pytesseract.image_to_data(255 - m, lang="spa", config="--psm 6", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, w in enumerate(d["text"]):
        if not w.strip() or float(d["conf"][i]) < 55 or d["height"][i] < 22 or d["height"][i] > 70: continue
        k = (d["block_num"][i], d["par_num"][i], d["line_num"][i]); x, y, ww, hh = d["left"][i], d["top"][i] + Y0, d["width"][i], d["height"][i]
        l = lines.setdefault(k, [x, y, x + ww, y + hh, []]); l[0] = min(l[0], x); l[1] = min(l[1], y); l[2] = max(l[2], x + ww); l[3] = max(l[3], y + hh); l[4].append(w)
    res[idx] = [[a, b, c2, d2, " ".join(ws)] for a, b, c2, d2, ws in lines.values() if len(ws) >= 1 and (c2 - a) > 60]
    print(idx, [r[4] for r in res[idx]], flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False)
