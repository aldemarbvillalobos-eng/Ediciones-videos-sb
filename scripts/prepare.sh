#!/usr/bin/env bash
# Uso: scripts/prepare.sh originales/<archivo>   (NO modifica el original)
# Genera en public/procesados/<slug>/:
#   source.mp4      copia de trabajo (video intacto, audio mejorado: highpass, denoise, EQ voz, compresión, loudnorm -16 LUFS)
#   audio16k.wav    audio mono 16 kHz para Whisper
#   info.json       metadatos (ffprobe)
#   silences.txt    silencios detectados (umbral adaptativo)
#   frames/         fotogramas de análisis cada N s
set -euo pipefail
IN="$1"
base="$(basename "$IN")"; slug="$(python3 -c 'import sys,unicodedata,re;s=unicodedata.normalize("NFKD",sys.argv[1]).encode("ascii","ignore").decode().lower();print(re.sub(r"[^a-z0-9]+","-",s).strip("-"))' "${base%.*}")"
OUT="public/procesados/$slug"; mkdir -p "$OUT/frames"
echo "slug=$slug"
ffprobe -v error -print_format json -show_format -show_streams "$IN" > "$OUT/info.json"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")

# 1) Medición de sonoridad y silencios adaptativos
thresh=$(ffmpeg -hide_banner -i "$IN" -map 0:a:0 -af loudnorm=print_format=json -f null - 2>&1 | grep '"input_thresh"' | grep -oE '[-0-9.]+')
ffmpeg -hide_banner -i "$IN" -map 0:a:0 -af "silencedetect=noise=${thresh}dB:d=0.45" -f null - 2>&1 | grep -E 'silence_(start|end)' > "$OUT/silences.txt" || true

# 2) Audio mejorado (dos pasadas de loudnorm)
CHAIN="highpass=f=80,afftdn=nr=12:nf=-50:tn=1,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2"
m=$(ffmpeg -hide_banner -i "$IN" -map 0:a:0 -af "$CHAIN,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
gv(){ echo "$m" | grep "\"$1\"" | grep -oE '[-0-9.]+' | head -1; }
LN="loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$(gv input_i):measured_TP=$(gv input_tp):measured_LRA=$(gv input_lra):measured_thresh=$(gv input_thresh):offset=$(gv target_offset):linear=true"
ffmpeg -hide_banner -loglevel error -y -i "$IN" -map 0:v:0 -map 0:a:0 -c:v copy -af "$CHAIN,$LN" -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT/source.mp4" \
 || ffmpeg -hide_banner -loglevel error -y -i "$IN" -map 0:v:0 -map 0:a:0 -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -af "$CHAIN,$LN" -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT/source.mp4"
ffmpeg -hide_banner -loglevel error -y -i "$OUT/source.mp4" -map 0:a:0 -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/audio16k.wav"

# 3) Fotogramas para análisis visual (≈ 40 por video)
step=$(python3 -c "print(max(2, round($dur/40, 1)))")
ffmpeg -hide_banner -loglevel error -y -i "$IN" -vf "fps=1/$step,scale=640:-2" -q:v 4 "$OUT/frames/f_%03d.jpg"
# 4) Estadísticas de luz/color
ffmpeg -hide_banner -i "$IN" -vf "fps=1,signalstats,metadata=print:key=lavfi.signalstats.YAVG" -f null - 2>&1 | grep -oE 'YAVG=[0-9.]+' | awk -F= '{s+=$2;n++} END{printf "YAVG medio=%.1f (0-255)\n", s/n}' > "$OUT/luma.txt"
echo "dur=$dur thresh=$thresh step=$step"; cat "$OUT/luma.txt"
