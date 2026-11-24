"""Fondo de estudio corporativo Sensation (procedural, sin IA generativa → sin problemas de licencia).
Estudio oscuro y elegante: ciclorama morado con textura, luz de recorte detrás del sujeto, paneles arquitectónicos
desenfocados con filo dorado, tiras LED doradas y luces prácticas (bokeh). Luminancia ajustada al original
para que la iluminación de la persona encaje.
Uso: make_studio_bg.py <salida.npy> [cx cy]"""
import sys, numpy as np, cv2
W, H = 1920, 1080; out = sys.argv[1]
cx = float(sys.argv[2]) if len(sys.argv) > 2 else 960; cy = float(sys.argv[3]) if len(sys.argv) > 3 else 420
hexrgb = lambda h: (np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255) ** 2.2  # lineal
INK, P1, P2, GOLD, BEIGE, TIERRA = map(hexrgb, ["#1E0B30", "#4B1D73", "#6A3FA0", "#A87B05", "#C5AE8A", "#74663A"])
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); t = yy / H
def blur(a, s): return cv2.GaussianBlur(a, (0, 0), s)
# 1) Ciclorama oscuro con textura de tela/pared (baja frecuencia)
tex = blur(rng.standard_normal((H // 8, W // 8)).astype(np.float32), 2.5); tex = cv2.resize(tex, (W, H), interpolation=cv2.INTER_CUBIC)
tex = 1 + 0.10 * tex / (np.abs(tex).max() + 1e-6)
img = INK[None, None] * (0.75 + 0.25 * (1 - t))[..., None] * tex[..., None]
# 2) Luz de fondo detrás del sujeto (spot elíptico, como en un set real)
r = np.sqrt(((xx - cx) / 700) ** 2 + ((yy - cy) / 520) ** 2)
img += P1[None, None] * (0.75 * np.exp(-r ** 2 * 1.3))[..., None] * tex[..., None]
img += P2[None, None] * (0.22 * np.exp(-r ** 2 * 3.0))[..., None]
# 3) Paneles arquitectónicos (profundidad): bloques verticales con borde iluminado, muy desenfocados
pan = np.zeros((H, W, 3), np.float32)
for x0, x1, lum in [(0, 300, 0.6), (330, 470, 0.35), (1480, 1600, 0.35), (1630, 1920, 0.6)]:
    m = np.zeros((H, W), np.float32); m[60:1080, x0:x1] = 1
    pan += P1[None, None] * (lum * 0.55 * m * (1.1 - t))[..., None]
    edge_x = x1 if x0 < 960 else x0
    e = np.exp(-((xx - edge_x) / 2.5) ** 2) * np.exp(-((yy - 380) / 420) ** 2)
    pan += GOLD[None, None] * (0.9 * e)[..., None]
img = img * 0.85 + blur(pan, 14)
# 4) Tiras LED doradas verticales (detalle premium discreto)
led = np.zeros((H, W), np.float32)
for x0 in (520, 1400):
    led[140:760, x0 - 1:x0 + 2] = np.hanning(620)[:, None] ** 0.7
img += (GOLD * 0.6 + BEIGE * 0.4)[None, None] * (blur(led, 4) * 2.4 + blur(led, 30) * 2.5)[..., None]
# 5) Luces prácticas lejanas (bokeh cálido)
bok = np.zeros((H, W, 3), np.float32)
for _ in range(12):
    x = rng.choice([rng.uniform(60, 430), rng.uniform(1500, 1860)]); y = rng.uniform(80, 520)
    rad = rng.uniform(14, 34); col = GOLD * 0.8 + BEIGE * 0.2; a = rng.uniform(0.03, 0.08)
    m = np.zeros((H, W), np.float32); cv2.circle(m, (int(x), int(y)), int(rad), 1.0, -1, cv2.LINE_AA)
    m = blur(m, rad * 0.22 + 1.0); ring = np.clip(m - blur(m, rad * 0.35) * 0.6, 0, 1)
    bok += col[None, None] * ((m * 0.8 + ring * 0.35) * a)[..., None]
img += bok
# 6) Viñeta, profundidad de campo y regreso a sRGB
vig = 1 - 0.7 * np.clip(np.sqrt(((xx - cx) / (W * 0.6)) ** 2 + ((yy - H * 0.42) / (H * 0.8)) ** 2) - 0.2, 0, 1) ** 1.5
img = blur(np.clip(img * vig[..., None], 0, 1), 2.5) ** (1 / 2.2)
img = np.clip(img, 0, 1).astype(np.float32)
np.save(out, img)
cv2.imwrite(out.replace(".npy", "_preview.png"), cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
L = (img * 255).mean(2); print("luma centro", L[300:600, 700:1200].mean().round(1), "bordes", L[:, :200].mean().round(1))
