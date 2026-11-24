#!/usr/bin/env bash
# Reinstala el entorno de IA (CPU) de forma reproducible. Idempotente.
set -euo pipefail
cd "$(dirname "$0")/.."
# 1) Sistema
apt-get install -y -qq tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng imagemagick libegl1 libgles2 libgl1 >/dev/null || echo "AVISO: apt falló (tesseract/imagemagick)"
# 2) Python 3.12 aislado
[ -d .venv-ai ] || uv venv -q --python 3.12 .venv-ai
VIRTUAL_ENV=.venv-ai uv pip install -q -r ai/requirements-ai.txt
VIRTUAL_ENV=.venv-ai uv pip install -q paddlepaddle paddleocr || echo "AVISO: PaddleOCR no se pudo instalar"
VIRTUAL_ENV=.venv-ai uv pip install -q --no-deps "git+https://github.com/facebookresearch/sam2.git" || echo "AVISO: SAM2 no se pudo instalar"
# 3) Modelos
.venv-ai/bin/python ai/download_models.py
# 4) Jost en TTF para rótulos de los comparativos (ffmpeg drawtext)
mkdir -p ai/cache && .venv-ai/bin/python -c "from fontTools.ttLib import TTFont; f=TTFont('public/brand/fonts/Jost-latin.woff2'); f.flavor=None; f.save('ai/cache/Jost.ttf')"
echo "Entorno IA listo. Diagnóstico: .venv-ai/bin/python ai/check_env.py"
