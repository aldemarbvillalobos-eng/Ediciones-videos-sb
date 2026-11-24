"""Control de calidad de la sustitución de fondo.
Uso: qc_composite.py <original> <t0> <t1> <compuesto.mp4> <alpha_dir> <bg.npy> <salida.json>
Mide: fidelidad de la persona (PSNR en el núcleo de la máscara), estabilidad temporal de la máscara,
halo en el borde exterior y conservación de subtítulos (OCR original vs compuesto)."""
import sys, json, av, numpy as np, cv2, pytesseract, difflib
src, t0, t1, comp, adir, bgp, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]
bg = np.load(bgp)
def frames(path, start, end):
    # por ORDINAL de fotograma (n/fps), independiente del start_time del contenedor
    c = av.open(path); s = c.streams.video[0]; fps_ = float(s.average_rate)
    for n_, fr in enumerate(c.decode(s)):
        t = n_ / fps_
        if t < start - 1e-3: continue
        if t > end + 1e-3: break
        yield t, fr.to_ndarray(format="rgb24").astype(np.float32) / 255
fps = 30.0; psnr = []; flick = []; halo = []; ocr = []; prev = None
for (to, O), (tc, Cimg) in zip(frames(src, t0, t1), frames(comp, 0, t1 - t0)):
    idx = round(to * fps); a = cv2.imread(f"{adir}/alpha_{idx:05d}.png", 0).astype(np.float32) / 255
    core = cv2.erode((a > 0.99).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool); core[840:] = False  # excluye zona de subtítulos
    mse = ((O[core] - Cimg[core]) ** 2).mean(); psnr.append(10 * np.log10(1 / max(mse, 1e-10)))
    if prev is not None:
        band = cv2.dilate(((a > 0.05) & (a < 0.95)).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        motion = np.abs(O - prev[1]).mean(2)[band].mean(); flick.append((np.abs(a - prev[0])[band].mean(), motion))
    ring = cv2.dilate((a > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~cv2.dilate((a > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ring[840:] = False; halo.append(float(np.abs(Cimg[ring] - bg[ring]).mean()))
    if idx % 30 == 0:
        def txt(img):
            g = cv2.cvtColor((img[860:] * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY); m = cv2.threshold(g, 185, 255, cv2.THRESH_BINARY_INV)[1]
            return " ".join(pytesseract.image_to_string(m, lang="spa", config="--psm 6").split())
        a1, b1 = txt(O), txt(Cimg); ocr.append({"t": round(to, 2), "original": a1, "compuesto": b1, "similitud": round(difflib.SequenceMatcher(None, a1, b1).ratio(), 3)})
    prev = (a, O)
fl = np.array(flick)
rep = {
    "frames": len(psnr),
    "persona_psnr_db": {"media": round(float(np.mean(psnr)), 2), "minimo": round(float(np.min(psnr)), 2)},
    "mascara_variacion_media_borde": round(float(fl[:, 0].mean()), 4),
    "mascara_variacion_p99_borde": round(float(np.percentile(fl[:, 0], 99)), 4),
    "correlacion_variacion_vs_movimiento": round(float(np.corrcoef(fl[:, 0], fl[:, 1])[0, 1]), 3),
    "halo_borde_exterior_media": round(float(np.mean(halo)), 4),
    "subtitulos_ocr_similitud_media": round(float(np.mean([o["similitud"] for o in ocr])), 3),
    "subtitulos_ocr": ocr,
}
json.dump(rep, open(out, "w"), ensure_ascii=False, indent=1); print(json.dumps({k: v for k, v in rep.items() if k != "subtitulos_ocr"}, indent=1))
