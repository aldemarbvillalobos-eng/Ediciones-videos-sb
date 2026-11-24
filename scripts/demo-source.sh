#!/usr/bin/env bash
# Genera la fuente sintética usada por la composición "Plantilla" (prueba técnica del motor).
mkdir -p public/procesados/_demo
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "testsrc2=s=1920x1080:r=30:d=20" -f lavfi -i "sine=f=220:d=20" \
  -vf "eq=brightness=-0.08" -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest public/procesados/_demo/source.mp4
