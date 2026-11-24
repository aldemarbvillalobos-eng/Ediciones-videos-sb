"""SAM 2.1 (tiny) como máscara-guía de persona en un tramo y zona concretos (p. ej. donde había un rótulo).
Puntos positivos: rostro y torso (de la alfa RVM). Puntos negativos: sobre el gráfico a excluir.
Uso: sam2_gate.py <video> <t0> <t1> <alpha_dir> <x_neg,y_neg;...> <salida_dir>"""
import sys, os, av, numpy as np, cv2, torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
src, t0, t1, adir, negs, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
neg = [tuple(map(int, p.split(","))) for p in negs.split(";")]; os.makedirs(out, exist_ok=True); torch.set_num_threads(4)
pred = SAM2ImagePredictor(build_sam2("configs/sam2.1/sam2.1_hiera_t.yaml", os.path.join(os.path.dirname(__file__), "models", "sam2.1_hiera_tiny.pt"), device="cpu"))
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate); c.seek(int(max(0, t0 - 1) / s.time_base), stream=s, backward=True)
n = 0
with torch.inference_mode():
    for fr in c.decode(s):
        t = float(fr.pts * s.time_base); idx = round(t * fps)
        if t < t0 - 1e-3: continue
        if t > t1: break
        img = fr.to_ndarray(format="rgb24"); a = cv2.imread(f"{adir}/alpha_{idx:05d}.png", 0)
        ys, xs = np.where(a[:820] > 200); cx = int(np.median(xs)); top = ys.min()
        pos = [(cx, top + 150), (cx, top + 420), (cx, top + 650)]
        pred.set_image(img)
        m, sc, _ = pred.predict(point_coords=np.array(pos + neg), point_labels=np.array([1] * len(pos) + [0] * len(neg)), multimask_output=False)
        cv2.imwrite(f"{out}/gate_{idx:05d}.png", (m[0] > 0).astype(np.uint8) * 255); n += 1
print("SAM2:", n, "máscaras →", out)
