"""Ensambla el máster del contenido (sin intro ni cierre) con la línea de tiempo EXACTA del original:
tramos de presentadora compuestos, diapositivas reconstruidas y transiciones de marca en lugar de los
destellos originales. Sobre las diapositivas y transiciones repinta los subtítulos ORIGINALES
(texto y caja) a partir de un fotograma representativo de cada subtítulo. Audio: el original, sin reprocesar.
Uso: assemble_master.py <config.json>
Config: fps, t0, t1, original, events (ordinal), boxOpacity, boxPad, out,
  clips: [{kind:"video", path, start, end, fileT0}]   (fileT0 = tiempo maestro del primer fotograma del archivo)
  trans: [{start, end, from:{path,fileT0,freezeAt}, to:{path,fileT0,freezeAt?}}]
  subsOn: [[start,end], ...]  tramos donde se repintan los subtítulos"""
import sys, json, subprocess, av, numpy as np, cv2
cfg = json.load(open(sys.argv[1])); fps = cfg["fps"]; t0, t1 = cfg["t0"], cfg["t1"]; W, H = 1920, 1080
ev = {int(k): v for k, v in json.load(open(cfg["events"])).items()}; K = cfg.get("boxOpacity", 0.18); PAD = cfg.get("boxPad", [14, 10, 14, 10])

class Reader:  # lectura secuencial por ordinal con caché
    def __init__(s, path, fileT0): s.c = av.open(path); s.it = s.c.decode(s.c.streams.video[0]); s.n = -1; s.cur = None; s.t0 = fileT0
    def at(s, T):
        want = max(0, round((T - s.t0) * fps))
        while s.n < want:
            try: s.cur = next(s.it).to_ndarray(format="rgb24"); s.n += 1
            except StopIteration: break
        return s.cur
readers = {}
def frame(path, fileT0, T):
    key = (path, fileT0)
    if key not in readers: readers[key] = Reader(path, fileT0)
    return readers[key].at(T)
def frozen(path, fileT0, T):  # fotograma congelado (lector aparte)
    r = Reader(path, fileT0); return r.at(T).copy()

# Capas de subtítulo por evento a partir del original: fotograma más oscuro del evento (fondo limpio)
orig = av.open(cfg["original"]); ostream = orig.streams.video[0]
def events_at(idx):
    return ev.get(idx, [])
sig = lambda boxes: " / ".join(b[4] for b in boxes)
need = {}
for s_, e_ in cfg["subsOn"]:
    for idx in range(round(s_ * fps), round(e_ * fps) + 1):
        b = events_at(idx)
        if b: need.setdefault(sig(b), set()).add(idx)
cands = {k: sorted(v) for k, v in need.items()}
layers = {}
best = {}
for n, fr in enumerate(orig.decode(ostream)):
    if n > round(t1 * fps): break
    b = events_at(n)
    if not b or sig(b) not in cands: continue
    img = fr.to_ndarray(format="rgb24").astype(np.float32) / 255; L = img.mean(2)
    if L.mean() > 0.32: continue  # destello: descartado
    score = 0; boxes = []
    for x0, y0, x1, y1, *_ in b:
        X0, Y0, X1, Y1 = max(0, x0 - PAD[0]), max(0, y0 - PAD[1]), min(W, x1 + PAD[2]), min(H, y1 + PAD[3]); boxes.append((X0, Y0, X1, Y1))
        reg = L[Y0:Y1, X0:X1]; score += np.percentile(reg, 40)
    if sig(b) not in best or score < best[sig(b)][0]:
        ta = np.zeros((H, W), np.float32)
        for X0, Y0, X1, Y1 in boxes:
            reg = L[Y0:Y1, X0:X1]; sat = img[Y0:Y1, X0:X1].max(2) - img[Y0:Y1, X0:X1].min(2)
            Lb = cv2.blur(cv2.erode(reg, np.ones((9, 9), np.uint8)), (9, 9))
            tt = np.clip((reg - Lb) / np.maximum(1 - Lb, 0.2), 0, 1) * (sat < 0.25)
            ta[Y0:Y1, X0:X1] = np.clip((tt - 0.10) / 0.75, 0, 1)
        best[sig(b)] = (score, boxes, ta, n)
print("capas de subtítulo:", {k[:40]: v[3] for k, v in best.items()})

def in_ranges(T, rs): return any(a - 1e-6 <= T < b - 1e-6 for a, b in rs)
def subs_for(idx):
    b = events_at(idx)
    if b and sig(b) in best: return best[sig(b)]
    # transición (destello): usar el subtítulo vecino (antes en la primera mitad, después en la segunda)
    for d in range(1, 25):
        for j in (idx - d, idx + d):
            bb = events_at(j)
            if bb and sig(bb) in best: return best[sig(bb)]
    return None

enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
    "-ss", str(t0), "-t", str(t1 - t0), "-i", cfg["original"], "-map", "0:v", "-map", "1:a",
    "-af", f"afade=t=out:st={t1 - t0 - 1.0}:d=1.0", "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "320k", "-shortest", cfg["out"]], stdin=subprocess.PIPE)
freeze_cache = {}
N = round((t1 - t0) * fps)
gold = np.array([168, 123, 5], np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); glow = np.exp(-(((xx - W * 0.5) / (W * 0.45)) ** 2 + ((yy - H * 0.45) / (H * 0.5)) ** 2))[..., None]
for n in range(N):
    T = t0 + n / fps; idx = round(T * fps); out = None
    for tr in cfg["trans"]:
        if tr["start"] - 1e-6 <= T < tr["end"] - 1e-6:
            a = tr["from"]; b = tr["to"]
            ka = ("f", a["path"], a["freezeAt"])
            if ka not in freeze_cache: freeze_cache[ka] = frozen(a["path"], a["fileT0"], a["freezeAt"]).astype(np.float32) / 255
            A = freeze_cache[ka]
            if b.get("freezeAt") is not None:
                kb = ("f", b["path"], b["freezeAt"])
                if kb not in freeze_cache: freeze_cache[kb] = frozen(b["path"], b["fileT0"], b["freezeAt"]).astype(np.float32) / 255
                B = freeze_cache[kb]
            else:
                B = frame(b["path"], b["fileT0"], T).astype(np.float32) / 255
            p = (T - tr["start"]) / (tr["end"] - tr["start"]); w = p * p * (3 - 2 * p)
            out = A * (1 - w) + B * w + gold * glow * (0.22 * np.sin(np.pi * p))  # fundido con destello dorado suave
            break
    if out is None:
        for cl in cfg["clips"]:
            if cl["start"] - 1e-6 <= T < cl["end"] - 1e-6:
                out = frame(cl["path"], cl["fileT0"], T).astype(np.float32) / 255; break
    if out is None: raise SystemExit(f"sin fuente para T={T}")
    if in_ranges(T, cfg["subsOn"]):
        L_ = subs_for(idx)
        if L_ is not None:
            _, boxes, ta, _ = L_
            for X0, Y0, X1, Y1 in boxes: out[Y0:Y1, X0:X1] *= (1 - K)
            out = out * (1 - ta[..., None]) + ta[..., None]
    enc.stdin.write((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    if n % 300 == 0: print("frame", n, "/", N, flush=True)
enc.stdin.close(); enc.wait(); print("máster →", cfg["out"])
