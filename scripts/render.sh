#!/usr/bin/env bash
# Uso: scripts/render.sh <IdComposicion>  → salida/<IdComposicion>.mp4 + control de calidad
set -euo pipefail
ID="$1"; OUT="salida/$ID.mp4"; QC="salida/qc-$ID"; mkdir -p salida "$QC"
npx remotion render "$ID" "$OUT" --codec=h264 --crf=16 --x264-preset=slow \
  --audio-codec=aac --audio-bitrate=320k --color-space=bt709 --pixel-format=yuv420p --concurrency=4 --log=error
# Control de calidad
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,bit_rate -show_entries format=duration,size -of compact "$OUT" | tee "$QC/probe.txt"
ffmpeg -hide_banner -i "$OUT" -map 0:a -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input (Integrated|True Peak)" | tee "$QC/loudness.txt"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
step=$(python3 -c "print(max(1, $dur/16))")
ffmpeg -hide_banner -loglevel error -y -i "$OUT" -vf "fps=1/$step,scale=480:-2,tile=4x4" -frames:v 1 "$QC/hoja-contactos.jpg"
echo "OK → $OUT"
