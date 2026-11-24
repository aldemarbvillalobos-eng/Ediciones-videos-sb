#!/usr/bin/env bash
# Genera los entregables de una prueba de identidad visual avanzada.
# Uso: scripts/entregables-prueba.sh <original> <t0> <t1> <id_composicion> <dir_salida> <inicio_cuerpo_s>
#   inicio_cuerpo_s = segundo del render de Remotion donde empieza el contenido (tras la intro)
set -euo pipefail
SRC="$1"; T0="$2"; T1="$3"; ID="$4"; OUT="$5"; BODY="$6"; DUR=$(python3 -c "print(round($T1-$T0,3))")
FONT=ai/cache/Jost.ttf; mkdir -p "$OUT/capturas"
Q="-c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -r 30 -c:a aac -b:a 320k -movflags +faststart"
# 1) Fragmento original (recorte exacto, sin cambios)
ffmpeg -hide_banner -loglevel error -y -ss "$T0" -t "$DUR" -i "$SRC" $Q "$OUT/01_original_fragmento.mp4"
# 2) Video con identidad Sensation (render Remotion: intro + fragmento + cierre)
npx remotion render "$ID" "$OUT/02_sensation_identidad.mp4" --codec=h264 --crf=16 --x264-preset=slow --audio-codec=aac --audio-bitrate=320k --color-space=bt709 --pixel-format=yuv420p --concurrency=4 --log=error
# 3) Comparativo antes / después (mismo tramo, sincronizado, audio original)
ffmpeg -hide_banner -loglevel error -y -i "$OUT/01_original_fragmento.mp4" -ss "$BODY" -t "$DUR" -i "$OUT/02_sensation_identidad.mp4" -filter_complex "\
[0:v]scale=944:-2,setsar=1[a];[1:v]setpts=PTS-STARTPTS,scale=944:-2,setsar=1[b];\
color=c=0x1E0B30:s=1920x1080:r=30:d=$DUR[bg];[bg][a]overlay=16:268[t1];[t1][b]overlay=960:268[t2];\
[t2]drawtext=fontfile=$FONT:text='ANTES · original':fontcolor=0xC5AE8A:fontsize=34:x=16+(944-tw)/2:y=200,\
drawtext=fontfile=$FONT:text='DESPUÉS · identidad Sensation Academy':fontcolor=white:fontsize=34:x=960+(944-tw)/2:y=200,\
drawbox=x=960:y=246:w=944:h=3:color=0xA87B05:t=fill,\
drawtext=fontfile=$FONT:text='Prueba técnica · DLU2_02_APL · contenido original de John C. Maxwell':fontcolor=0xC5AE8A@0.8:fontsize=24:x=(w-tw)/2:y=850[v]" \
  -map "[v]" -map 0:a $Q -t "$DUR" "$OUT/03_comparativo_antes_despues.mp4"
# 4) Capturas en alta resolución (1920×1080 PNG) original vs editado en puntos clave
for s in 1.5 4.0 9.0 15.0 21.0 25.5; do
  n=$(printf "%04.1f" "$s" | tr . _)
  ffmpeg -hide_banner -loglevel error -y -ss "$s" -i "$OUT/01_original_fragmento.mp4" -frames:v 1 "$OUT/capturas/t${n}_original.png"
  ffmpeg -hide_banner -loglevel error -y -ss "$(python3 -c "print($BODY+$s)")" -i "$OUT/02_sensation_identidad.mp4" -frames:v 1 "$OUT/capturas/t${n}_sensation.png"
done
ffmpeg -hide_banner -loglevel error -y -ss 1 -i "$OUT/02_sensation_identidad.mp4" -frames:v 1 "$OUT/capturas/intro.png"
ffmpeg -hide_banner -loglevel error -y -sseof -1.5 -i "$OUT/02_sensation_identidad.mp4" -frames:v 1 "$OUT/capturas/cierre.png"
ls -la "$OUT" "$OUT/capturas"
