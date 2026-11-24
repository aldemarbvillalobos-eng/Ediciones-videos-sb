# Registro de modelos de IA (entorno de edición de Sensation Academy)

Entorno: CPU x86_64 con 4 núcleos (AVX-512), 15 GB de RAM y **sin GPU**: no hay CUDA ni MPS. Todo se ejecuta en CPU con PyTorch 2.15 (cpu).
Los modelos se guardan en `ai/models/` y el código de terceros en `ai/vendor/`. Ninguno de los dos se versiona: se descargan con `scripts/setup-ai.sh`.

| Modelo | Versión / archivo | Fuente oficial | Licencia | Tamaño | Memoria aprox. | CPU / GPU | Prueba (nov. 2026) | Uso |
|---|---|---|---|---|---|---|---|---|
| Robust Video Matting ResNet50 | v1.0.0 `rvm_resnet50.pth` | github.com/PeterL1n/RobustVideoMatting (releases) | GPL-3.0 (código y pesos) | 103 MB | ~2 GB a 1080p (downsample 0,25) | CPU ✔ / CUDA ✔ | ✔ 3,8 fps sin carga (≈2 fps con carga). Mejor borde de cabello | **Principal**: recorte temporal de la persona |
| Robust Video Matting MobileNetV3 | v1.0.0 `rvm_mobilenetv3.pth` | ídem | GPL-3.0 | 15 MB | ~1 GB | CPU ✔ / CUDA ✔ | ✔ 6,3 fps. Cabello algo más tosco | Alternativa rápida y borradores |
| SAM 2.1 Hiera Tiny | `sam2.1_hiera_tiny.pt` (sept. 2024) | github.com/facebookresearch/sam2 · dl.fbaipublicfiles.com | Apache-2.0 | 149 MB | ~2,5 GB | CPU ✔ (lento) / CUDA ✔ | ✔ ≈1,6 s por fotograma. Máscara binaria (borde duro) | Máscara guía en zonas concretas (rótulos) |
| MediaPipe Selfie Multiclass 256 | `selfie_multiclass_256x256.tflite` (float32) | storage.googleapis.com/mediapipe-models | Apache-2.0 (repositorio MediaPipe; ficha del modelo no revisada) | 16 MB | <500 MB | CPU ✔ | ✔ 0,2–0,5 s por fotograma. Máscara blanda que deja ver el fondo | Descartado para el recorte; queda como apoyo de detección |
| MediaPipe Selfie Segmenter | `selfie_segmenter.tflite` (float16) | ídem | Apache-2.0 (ídem) | 0,25 MB | mínima | CPU ✔ | descargado, sin uso | Reserva |
| PaddleOCR PP-OCRv5 mobile (det + rec en) | descarga automática a `~/.paddlex/official_models` | github.com/PaddlePaddle/PaddleOCR | Apache-2.0 | ~20 MB | <1 GB | CPU ✔ (requiere `enable_mkldnn=False`) | ✔ leyó "TRACI MORROW / BUSINESS OWNER / ENTREPRENEUR" con confianza 0,96–1,0 | OCR de rótulos (comprobación cruzada) |
| Tesseract 5.3.4 + spa/eng | paquete apt `tesseract-ocr-spa` | github.com/tesseract-ocr | Apache-2.0 | ~25 MB | mínima | CPU ✔ | ✔ OCR por segundo y cajas de subtítulos | OCR de subtítulos y títulos |
| Whisper large-v3-turbo (whisper.cpp 1.7.6) | `ggml-large-v3-turbo.bin` | github.com/ggerganov/whisper.cpp · OpenAI | MIT | 1,6 GB | ~2 GB | CPU ✔ | ✔ ya en uso | Transcripción y análisis del audio |

## Evaluados y no instalados
- **ProPainter** (reconstrucción temporal): su licencia S-Lab 1.0 **no permite uso comercial**, así que no se instaló. Las reconstrucciones necesarias se resolvieron con OpenCV (inpainting Telea, relleno por convolución normalizada y placa de fondo por mediana temporal).
  - Alternativa compatible si alguna vez hace falta reconstruir zonas grandes: **LaMa** (Apache-2.0). No es necesaria por ahora.
- **faster-whisper** (MIT): la librería está instalada, pero no se descargó su modelo porque whisper.cpp ya cubre la transcripción.

## Notas de licencia
- **RVM es GPL-3.0.** Se usa como herramienta interna para procesar los videos; los videos resultantes no quedan sujetos a la GPL. Si alguna vez se distribuye el código de RVM, modificado o no, hay que cumplir la GPL-3.0.
- Ningún modelo se sube a GitHub (`.gitignore`: `ai/models/`, `ai/vendor/`, `.venv-ai/`).
