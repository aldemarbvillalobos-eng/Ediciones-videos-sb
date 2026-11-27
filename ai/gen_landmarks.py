"""Puntos faciales (MediaPipe) de la cabeza generada, en coordenadas del fotograma (para la corrección geométrica V3).
Uso: gen_landmarks.py <lp_dir>"""
import sys, json, numpy as np, cv2, os
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
D = sys.argv[1]; m = json.load(open(f"{D}/meta.json")); HERE = os.path.dirname(os.path.abspath(__file__))
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=f"{HERE}/models/face_landmarker.task"), num_faces=1))
out = {}
for f in m["frames"]:
    if not f.get("ok"): continue
    g = cv2.cvtColor(cv2.imread(f"{D}/gen/gen_{f['n']:05d}.png"), cv2.COLOR_BGR2RGB)
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=g))
    if not r.face_landmarks: continue
    P = np.array([[p.x * 512, p.y * 512] for p in r.face_landmarks[0]], np.float32)
    M = np.array(f["M_c2o"], np.float32)[:2]; Pf = P @ M[:, :2].T + M[:, 2]
    out[f["i"]] = {"chin": Pf[152].tolist(), "top": Pf[10].tolist(), "jawL": Pf[172].tolist(), "jawR": Pf[397].tolist(), "face_h": float(np.linalg.norm(Pf[10] - Pf[152]))}
json.dump(out, open(f"{D}/gen_landmarks.json", "w")); print("landmarks", len(out))
