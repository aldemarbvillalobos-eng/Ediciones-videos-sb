"""Descarga los modelos de IA desde fuentes oficiales a ai/models/ y clona el código de RVM en ai/vendor/.
Idempotente. Registro de licencias y pruebas: ai/MODELOS.md"""
import os, subprocess, urllib.request, hashlib, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
M = ROOT / "models"; V = ROOT / "vendor"; M.mkdir(exist_ok=True); V.mkdir(exist_ok=True)
FILES = {
    # Robust Video Matting (GPL-3.0) — releases oficiales PeterL1n/RobustVideoMatting v1.0.0
    "rvm_mobilenetv3.pth": "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3.pth",
    "rvm_resnet50.pth": "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50.pth",
    # SAM 2.1 (Apache-2.0) — Meta, checkpoint oficial
    "sam2.1_hiera_tiny.pt": "https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt",
    # MediaPipe Image Segmenter (Apache-2.0) — Google
    "selfie_multiclass_256x256.tflite": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
    "selfie_segmenter.tflite": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite",
}
for name, url in FILES.items():
    dst = M / name
    if dst.exists() and dst.stat().st_size > 0:
        print("ok (existe)", name); continue
    print("descargando", name); urllib.request.urlretrieve(url, dst)
    print("  ", dst.stat().st_size, "bytes sha256", hashlib.sha256(dst.read_bytes()).hexdigest()[:16])
if not (V / "RobustVideoMatting").exists():
    subprocess.check_call(["git", "clone", "-q", "--depth", "1", "https://github.com/PeterL1n/RobustVideoMatting.git", str(V / "RobustVideoMatting")])
print("Modelos listos en", M)
