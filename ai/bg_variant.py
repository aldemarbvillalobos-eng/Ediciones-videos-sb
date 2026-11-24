"""Variante del fondo de estudio para otro ángulo de cámara del MISMO set (continuidad visual):
escala alrededor del sujeto (plano más cerrado = fondo más grande) y desenfoque extra (menor profundidad de campo).
Uso: bg_variant.py <fondo.npy> <salida.npy> <zoom> <cx> <cy> [desenfoque_extra_px] [dx dy]"""
import sys, numpy as np, cv2
src, out, z, cx, cy = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
blur = float(sys.argv[6]) if len(sys.argv) > 6 else 3.0; dx = float(sys.argv[7]) if len(sys.argv) > 7 else 0; dy = float(sys.argv[8]) if len(sys.argv) > 8 else 0
bg = np.load(src); H, W = bg.shape[:2]
M = np.float32([[z, 0, (1 - z) * cx + dx], [0, z, (1 - z) * cy + dy]])
v = cv2.warpAffine(bg, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
if blur > 0: v = cv2.GaussianBlur(v, (0, 0), blur)
np.save(out, v.astype(np.float32)); cv2.imwrite(out.replace(".npy", "_preview.png"), cv2.cvtColor((np.clip(v, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
print("variante", out, "zoom", z)
