"""Compara segmentación en fotogramas concretos: RVM (de dir), MediaPipe, SAM2.1 tiny.
Uso: compare_seg.py <video> <frame_idx> <rvm_mb_dir> <rvm_r50_dir> <out_png>"""
import sys, os, time, av, numpy as np, cv2, torch
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, idx, d_mb, d_r50, outp = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
HERE = os.path.dirname(__file__)
c = av.open(src); s = c.streams.video[0]; fps = float(s.average_rate)
c.seek(int((idx / fps - 0.5) / s.time_base), stream=s, backward=True)
for fr in c.decode(s):
    if round(float(fr.pts * s.time_base) * fps) >= idx: img = fr.to_ndarray(format="rgb24"); break
H, W = img.shape[:2]; res = {}
res["RVM mobilenetv3"] = cv2.imread(f"{d_mb}/alpha_{idx:05d}.png", 0) / 255.0
res["RVM resnet50"] = cv2.imread(f"{d_r50}/alpha_{idx:05d}.png", 0) / 255.0
# MediaPipe multiclass (persona = 1 - fondo)
t = time.time()
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=f"{HERE}/models/selfie_multiclass_256x256.tflite"), output_confidence_masks=True))
r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=img)); res["MediaPipe multiclass"] = 1 - np.squeeze(r.confidence_masks[0].numpy_view()); seg.close(); print("mediapipe", round(time.time() - t, 2), "s")
# SAM2.1 tiny con puntos en rostro y torso (cuadro alrededor de la persona a partir de RVM)
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
t = time.time()
model = build_sam2("configs/sam2.1/sam2.1_hiera_t.yaml", f"{HERE}/models/sam2.1_hiera_tiny.pt", device="cpu")
pred = SAM2ImagePredictor(model); pred.set_image(img)
ys, xs = np.where(res["RVM resnet50"] > 0.5); box = np.array([xs.min(), ys.min(), xs.max(), ys.max()])
masks, scores, logits = pred.predict(box=box, point_coords=np.array([[int(np.median(xs)), int(ys.min() + 120)], [int(np.median(xs)), int(ys.min() + 500)]]), point_labels=np.array([1, 1]), multimask_output=False)
res["SAM2.1 tiny"] = masks[0].astype(float); print("sam2", round(time.time() - t, 2), "s")
purple = np.zeros_like(img, dtype=float); purple[:] = (75, 29, 115)
tiles = []
for k, a in res.items():
    a3 = a[..., None]; comp = (img * a3 + purple * (1 - a3)).astype(np.uint8)
    ys, xs = np.where(a > 0.5); cx = int(np.median(xs)); top = ys.min()
    hair = comp[max(0, top - 40): top + 360, cx - 320: cx + 320]
    hair = cv2.resize(hair, (640, 400))
    full = cv2.resize(comp, (640, 360))
    lab = np.zeros((40, 1280, 3), np.uint8); cv2.putText(lab, k, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    row = np.hstack([full, cv2.resize(hair, (640, 360))]); tiles.append(np.vstack([lab, row]))
cv2.imwrite(outp, cv2.cvtColor(np.vstack(tiles), cv2.COLOR_RGB2BGR))
