"""Diagnóstico del entorno de IA de edición. Uso: .venv-ai/bin/python ai/check_env.py"""
import importlib, os, platform, shutil, subprocess, sys
ok = lambda b: "OK " if b else "FALTA"
print("Python", sys.version.split()[0], "|", platform.platform())
print("CPU", os.cpu_count(), "| RAM", round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30, 1), "GB")
try:
    import torch; print("torch", torch.__version__, "| CUDA", torch.cuda.is_available(), "| MPS", getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(), "| hilos", torch.get_num_threads())
except Exception as e: print("torch FALTA", e)
for m in ["torchvision", "cv2", "av", "scenedetect", "numpy", "scipy", "skimage", "PIL", "mediapipe", "onnxruntime", "huggingface_hub", "transformers",
          "pytesseract", "paddleocr", "soundfile", "librosa", "pyloudnorm", "faster_whisper", "sam2"]:
    try: mod = importlib.import_module(m); print(ok(True), m, getattr(mod, "__version__", ""))
    except Exception as e: print(ok(False), m, type(e).__name__, str(e)[:80])
for b in ["ffmpeg", "ffprobe", "tesseract", "convert", "node", "npx"]:
    p = shutil.which(b); v = subprocess.run([b, "-version" if b in ("ffmpeg", "ffprobe", "convert") else "--version"], capture_output=True, text=True).stdout.splitlines()[0] if p else ""
    print(ok(bool(p)), b, v[:70])
M = os.path.join(os.path.dirname(__file__), "models")
for f in ["rvm_resnet50.pth", "rvm_mobilenetv3.pth", "sam2.1_hiera_tiny.pt", "selfie_multiclass_256x256.tflite", "selfie_segmenter.tflite"]:
    p = os.path.join(M, f); print(ok(os.path.exists(p)), "modelo", f, round(os.path.getsize(p) / 2**20, 1) if os.path.exists(p) else "", "MB")
print(ok(os.path.exists(os.path.join(os.path.dirname(__file__), "vendor", "RobustVideoMatting"))), "código RVM (ai/vendor)")
