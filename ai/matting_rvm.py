"""Robust Video Matting (recurrente, coherencia temporal) sobre un tramo del video.
Uso: .venv-ai/bin/python ai/matting_rvm.py <video> <inicio_s> <fin_s> <dir_salida> [mobilenetv3|resnet50] [downsample]
Guarda alpha_%05d.png (8 bits, índice = frame del ORIGINAL) y stats.json."""
import sys, os, time, json, av, torch, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "vendor", "RobustVideoMatting"))
from model import MattingNetwork
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
variant = sys.argv[5] if len(sys.argv) > 5 else "resnet50"; ds = float(sys.argv[6]) if len(sys.argv) > 6 else 0.25
os.makedirs(out, exist_ok=True); torch.set_num_threads(4)
m = MattingNetwork(variant).eval(); m.load_state_dict(torch.load(os.path.join(os.path.dirname(__file__), "models", f"rvm_{variant}.pth"), map_location="cpu"))
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate)
warm = max(0.0, t0 - 1.5)  # calentar el estado recurrente 1,5 s antes del tramo
c.seek(int(warm / s.time_base), stream=s, backward=True)
rec = [None] * 4; n = 0; tic = time.time()
with torch.inference_mode():
    for fr in c.decode(s):
        t = float(fr.pts * s.time_base)
        if t < warm - 1e-3: continue
        if t > t1: break
        x = torch.from_numpy(fr.to_ndarray(format="rgb24")).permute(2, 0, 1).float().div(255).unsqueeze(0)
        fgr, pha, *rec = m(x, *rec, downsample_ratio=ds)
        if t >= t0 - 1e-3:
            idx = round(t * fps); cv2.imwrite(os.path.join(out, f"alpha_{idx:05d}.png"), (pha[0, 0].numpy() * 255).round().astype(np.uint8)); n += 1
dt = time.time() - tic
json.dump({"model": f"rvm_{variant}", "downsample": ds, "frames": n, "seconds": round(dt, 1), "fps": round(n / dt, 2)}, open(os.path.join(out, "stats.json"), "w"))
print(f"rvm_{variant}: {n} frames en {dt:.1f}s ({n/dt:.2f} fps)")
