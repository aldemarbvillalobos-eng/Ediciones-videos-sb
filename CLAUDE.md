# Sensation Academy — Edición profesional de videos con Remotion

Actúa como **editor audiovisual profesional** (Remotion, motion graphics, contenido educativo y corporativo).
El usuario sube videos originales a `originales/`. Tu trabajo es **ejecutar** la edición y entregar el MP4 final, no explicar cómo hacerlo.
No crees otro editor ni otra aplicación. Usa el motor existente (`src/engine`, `src/brand`) y añade solo lo necesario para cada video.

## Reglas permanentes
- **Nunca** modifiques los archivos de `originales/`. Todo derivado va a `public/procesados/<slug>/`; las entregas van a `salida/`.
- No cambies el mensaje ni el significado. No inventes datos, nombres ni cargos: si no se dicen en el video o no los da el usuario, no los pongas.
- Conserva la resolución, orientación y fps originales salvo que se pida otro formato.
- No uses recursos de pago. Música: solo pistas que el usuario ponga en `public/musica/` o que haya autorizado expresamente. Si no hay, entrega sin música y dilo.
- El estilo es moderno, elegante, dinámico, educativo, corporativo y premium. Nada exagerado, solo colores de marca y transiciones que no distraigan.
- El ritmo depende del tipo de video: una capacitación lleva cortes limpios y pocas transiciones; uno promocional o motivacional, más dinamismo.
- Selecciona los elementos de marca que aporten. No es obligatorio usarlos todos.
- Antes de entregar, revisa los fotogramas: los textos no tapan rostros, se respetan los márgenes y la ortografía es correcta.

## Identidad visual (`src/brand/tokens.ts`)
- Morado #4B1D73 · Morado secundario #6A3FA0 · Dorado #A87B05 · Beige #C5AE8A · Blanco #FFFFFF. Fondo oscuro derivado: #1E0B30.
- Tipografía Jost, empaquetada en `public/brand/fonts` (OFL) para renderizar sin red.
- Logo oficial descargado de sensationacademy.net (wordmark "Sensation Brands"): `public/brand/logo-sensation-{blanco,negro}.png` y `favicon-sb.png`.
- Lema mostrado en la web: "Aprende. Crece. Brilla." Web: sensationacademy.net.
- Verificación (nov 2026): la web es un Moodle con un tema genérico (rojo #CA3120 y gris #212121) y no publica la paleta morado/dorado ni Jost. Esos valores son la **referencia corporativa del cliente** y son los que se aplican. El logo de la web es monocromo negro; sobre fondos morados se usa la versión blanca. Si el usuario aporta un manual de marca o un logo de "Sensation Academy", actualiza `tokens.ts` y `public/brand/`.

## Flujo por video
1. **Preparar** (sin tocar el original):
   `scripts/prepare.sh originales/<archivo>` → `public/procesados/<slug>/` con:
   `source.mp4` (video intacto + audio mejorado: filtro de graves, reducción de ruido, ecualización de voz, compresión y normalización a −16 LUFS), `audio16k.wav`, `info.json`, `silences.txt`, `frames/`, `luma.txt`.
2. **Transcribir**: `node scripts/transcribe.mjs <slug>` (whisper.cpp `large-v3-turbo`, español, palabra a palabra) → `captions.json` y `transcripcion.txt`.
   Si falta `whisper.cpp/`: `node scripts/setup-whisper.mjs` (unos 2 minutos y 1,6 GB).
3. **Analizar**: mira los fotogramas de `frames/` (encuadre, posición del rostro, luz, gráficos en pantalla) y lee la transcripción completa. Identifica silencios, muletillas, errores, repeticiones y tomas falsas (quédate con la última toma buena), los temas y los conceptos clave.
4. **Corregir el texto**: revisa `captions.json` (ortografía, tildes, nombres propios y puntuación) sin cambiar lo dicho.
5. **Decidir la edición** en `src/videos/<slug>.ts` (tipo `Edit`; ver `src/videos/_plantilla.ts`). Todos los tiempos van en segundos del original:
   - `segments`: lo que se conserva. Corta en pausas naturales, deja unos 0,10–0,15 s de aire antes y después de cada frase y elimina silencios de más de 0,4 s.
   - Alterna `zoom` 1 / 1.06–1.10 entre cortes consecutivos para disimular los saltos. Usa `pushIn` de 0,02–0,04 en los momentos importantes y `focus` sobre el rostro, según los fotogramas.
   - `wipeBefore` solo en los cambios de tema.
   - `overlays`: `lowerThird` (nombre y cargo, solo si se conocen), `card` (concepto clave con iconos de `brand/Icons.tsx`) y `chapter` (separador de tema). Colócalos en el lado libre del encuadre.
   - `keywords`: términos que se destacan en los subtítulos. `color`: corrección con `colorCorrection` solo si hace falta (por ejemplo, `luma.txt` con YAVG < 90 indica un video oscuro).
   - Para incluir los subtítulos, importa `public/procesados/<slug>/captions.json` (ruta relativa).
6. **Registrar** el `<Composition>` en `src/Root.tsx` (carpeta "Entregas", id = slug).
7. **Revisar** con `npx remotion still <id> --frame=N` en los puntos clave (rótulos, tarjetas, transiciones) y corrige lo necesario.
8. **Renderizar**: `scripts/render.sh <id>` → `salida/<id>.mp4` (H.264 CRF 16, preset slow, AAC 320k, bt709) y control de calidad en `salida/qc-<id>/` (sonoridad y hoja de contactos). Revisa la hoja de contactos.
9. **Entregar**: resume brevemente los cambios y la ubicación del archivo.

## Notas técnicas
- Chromium no confía en el proxy del contenedor: no cargues fuentes ni recursos remotos en el render. Todo debe estar en `public/`.
- `originales/`, `salida/`, `public/procesados/` y `whisper.cpp/` no se versionan (archivos pesados).
- Rendimiento: unos 5 s de render por cada segundo de video (4 CPU). Los renders largos se lanzan en segundo plano.
- Comprobación de tipos: `npx tsc --noEmit`.

## Curso "Desarrolle el líder que está en usted" (John C. Maxwell) — decisiones del cliente
- El material tiene licencia para añadir la marca y para editarlo. Ya viene producido de forma profesional: audio en inglés con subtítulos en español incrustados.
- Se hace **adaptación corporativa**: intro premium (curso, lección y crédito "Contenido original de John C. Maxwell"), logo discreto arriba a la derecha solo entre las cortinillas originales (`watermarkRange`) y cierre con sensationacademy.net y "Aprende. Crece. Brilla.".
- Prohibido: subtítulos nuevos, gráficos o animaciones sobre los gráficos originales, cortes que alteren el contenido y simular o tapar imágenes dañadas. Se mantienen 1920×1080 a 30 fps.
- **Intro original:** si la licencia permite sustituirla, se elimina y solo queda la intro de Sensation Academy (nunca dos intros seguidas). El punto de inicio se fija analizando el original:
  - el fin del título o el fundido a negro (`signalstats` YAVG por fotograma);
  - el fin de la música de la intro (`astats` RMS);
  - la primera palabra (`silences.txt`).

  Empieza después de la música y del título y unos 0,7 s antes de la primera palabra, sin cortar contenido. Usa un fundido cruzado `introTransitionF: 20` hacia el contenido. Documenta los tiempos en `src/videos/<slug>.ts`.
- Audio y video originales sin reprocesar: copia sin recodificar a `public/procesados/<slug>/original.mp4`.
- Muestra aprobada pendiente: `dlu2-02-apl-muestra`. Si se aprueba, renderizar `dlu2-02-apl` (completo).
- DLU2_01_LEC.mp4 (md5 2f85592e…): 83 paquetes H.264 inválidos entre 1192,3 y 1195,0 s (no recuperables) y ningún dato de video después de 1195 s (el audio sigue hasta 1709 s).
  - **Pedido del cliente:** editar solo la intro (intro de Sensation y logo discreto) y dejar el resto igual. Se entrega `salida/dlu2-01-lec-intro-sb.mp4`:
    - intro de Sensation y fundido de 0,6 s hacia el contenido, que empieza en 12,07 s (la cortinilla original termina en 12,05 s y la primera palabra llega a 12,22 s);
    - contenido original con el logo hasta 1192,0 s, el último tramo íntegro; ahí termina la imagen que tiene el archivo (el cliente confirmó que es la única copia y pidió dejarla hasta donde llegue);
    - fundido de 0,6 s al cierre de Sensation, que marca el final;
    - sin fondo nuevo ni rótulos nuevos.
  - No se simulan imágenes. El tramo dañado y los 8,5 min de solo audio quedan pendientes de una copia íntegra.
  - Script: `public/procesados/dlu2-01-lec/render_lec.sh` (FFmpeg, una pasada).

## Edición avanzada con IA: sustitución de fondo y rediseño gráfico
Cuándo se aplica: el cliente autorizó, dentro de la licencia del curso, sustituir el fondo y rediseñar los gráficos conservando a las personas, sus voces, los subtítulos y la autoría. Registro de modelos y licencias: `ai/MODELOS.md`.

### Entorno (reproducible)
- **Instalación:** `scripts/setup-ai.sh` instala:
  - paquetes del sistema por apt: tesseract-ocr con español e inglés, imagemagick, libegl1, libgles2 y libgl1;
  - un entorno Python 3.12 aislado en `.venv-ai/` (con `uv`), a partir de `ai/requirements-ai.txt` (PyTorch CPU);
  - PaddleOCR y SAM 2;
  - los modelos, con `ai/download_models.py`.
- **Diagnóstico:** `.venv-ai/bin/python ai/check_env.py`.
- **Hardware:** solo CPU (sin CUDA ni MPS). Todo se procesa por tramos y los resultados intermedios se guardan en `ai/cache/<slug>/` (no versionado).
- **Notas:**
  - PaddleOCR en CPU necesita `enable_mkldnn=False`.
  - MediaPipe necesita libEGL.
  - Al ejecutar Tesseract en paralelo con otros procesos, usa `OMP_THREAD_LIMIT=1`.

### Flujo por video o tramo (comandos)
1. **Diagnóstico y escenas:**
   - `.venv-ai/bin/scenedetect -i <video> -o ai/cache/<slug> detect-adaptive list-scenes`.
   - OCR por segundo: `ai/ocr_scan.py`, que localiza títulos, rótulos, subtítulos y diapositivas.
2. **Segmentación de la persona:** `ai/matting_rvm.py <video> t0 t1 ai/cache/<slug>/alpha_rvm_r50 resnet50 0.25`. RVM ResNet50 fue el ganador de la comparación de `ai/compare_seg.py`, frente a MobileNetV3, MediaPipe y SAM 2.
3. **Subtítulos incrustados:**
   - `OMP_THREAD_LIMIT=1 ai/subs_boxes.py … 6` y luego `ai/subs_events.py` → eventos estables con cajas por línea.
   - Excluye palabras de rótulos que el OCR fusione con los subtítulos.
4. **Copia de análisis sin subtítulos:** `ai/preclean_subs.py` (inpainting de las letras). **Imprescindible**: sin ella, RVM corta el cuerpo bajo la franja de subtítulos. RVM se ejecuta sobre esta copia.
5. **Rótulos o gráficos originales a sustituir:** `ai/preclean_overlay.py` (config con `rect`, `win`, `plate`, `alpha` y `subs`).
   - Placa de fondo por mediana temporal, solo con píxeles de fondo y fuera de las cajas de subtítulos.
   - Gráfico sobre el fondo → placa. Gráfico sobre la persona → relleno por convolución normalizada.
   - Si quedan restos sobre la persona, el rótulo nuevo de Sensation se coloca en **la misma zona y el mismo tramo** (props `x`/`y` del overlay `lowerThird`) para cubrirlos.
   - `ai/sam2_gate.py` queda como herramienta de apoyo.
6. **Fondo de estudio:** `ai/make_studio_bg.py <out.npy> cx cy`. Es procedural (sin IA generativa ni problemas de licencia) y su luminancia está ajustada a la del set original. Haz un fondo por ángulo de cámara.
7. **Composición:** `ai/composite_bg.py <config.json>`. Toma la persona de los píxeles originales y hace:
   - descontaminación de bordes y envoltura de luz;
   - reconstrucción de la caja de subtítulos (opacidad real ≈0,18) y repintado del texto original con su alfa;
   - grano de película;
   - mezcla con el audio original.

   Salida: `public/procesados/<slug>/fragmento_estudio.mp4`.
8. **Remotion:** composición con el `Edit` de `src/videos/<slug>-estudio.ts`: intro, rótulo rediseñado, logo y cierre.
9. **Control de calidad:** `ai/qc_composite.py` mide:
   - el PSNR de la persona, que debe ser alto: sus píxeles no se modifican;
   - la estabilidad temporal de la máscara;
   - el halo;
   - el OCR de los subtítulos antes y después.

   Revisa además fotogramas ampliados: cabello, manos, la zona del rótulo antiguo y el borde inferior.
10. **Entregables:** `scripts/entregables-prueba.sh` genera, en `salida/<prueba>/`, el original, el editado, el comparativo y las capturas.

### Reglas
- No regeneres ni alteres a las personas: nada de intercambio facial ni retoque de apariencia. MediaPipe solo sirve para detección.
- No uses ProPainter en producción (licencia no comercial). Usa OpenCV o, si hiciera falta, LaMa (Apache-2.0).
- Confirma visualmente el OCR antes de reescribir nombres o cargos. Conserva el texto exacto del original.
- No elimines créditos ni avisos de derechos que deban conservarse. Mantén el crédito a John C. Maxwell en la intro y en el cierre.

### Video completo: estilo aprobado y estándar para todos los videos del curso
**Aprobado por el cliente (nov. 2026)**:
- fondo de estudio morado con paneles desenfocados, tiras LED doradas y luces cálidas;
- rótulos en Jost con fondo morado y línea dorada;
- diapositivas reconstruidas;
- intro y cierre de Sensation.

No cambies este diseño ni experimentes con estilos nuevos sin autorización. Con cada video nuevo en `originales/` el proceso es:
1. **Integridad:** `ffprobe` (duraciones de video y audio), decodificación completa (`ffmpeg -v error -f null`) y validación de paquetes si hay errores. Si el archivo está dañado, informa y no ocultes el daño.
2. **Estructura:** mide brillo y diferencia por fotograma para detectar cortes, destellos y cambios de plano. Mide los tiempos de aparición de cada línea de diapositiva por fotograma, después de los destellos.
3. **Subtítulos:** `subs_boxes.py` (cada 3 frames) y luego `subs_events.py`. El filtro acepta líneas cortas como "¿Y tú?" o "en consecuencia.". Excluye las palabras de los rótulos.
4. **Índices de fotograma:** algunos MP4 originales empiezan con `start_time` > 0 (DLU2_02_APL: 0,066 s, es decir, 2 frames). Las copias de trabajo usan **ordinal** (n/fps). Convierte los eventos del OCR (índice por pts) a ordinal antes de usarlos sobre las copias (`*_ord.json`). El audio con `ffmpeg -ss T` sobre el original queda alineado con el ordinal (verificado).
5. **Persona:** `preclean_overlay.py` (rótulos) → `preclean_subs.py` (copia de análisis) → `matting_rvm.py` por plano → `composite_bg.py` con `bgRanges` por plano. Fondo del primer plano: `ai/bg_variant.py` (mismo set, zoom ≈1,45 y más desenfoque).
6. **Diapositivas:** `src/brand/SlideList.tsx`, con el texto exacto y los tiempos medidos (composiciones en la carpeta "Diapositivas" de `Root.tsx`). Se renderizan sin audio en `ai/cache/<slug>/`.
7. **Máster:** `ai/assemble_master.py`. Mantiene la línea de tiempo exacta del original y hace:
   - sustituye los destellos originales por fundidos con un destello dorado suave;
   - repinta los subtítulos originales (texto y caja, desde el fotograma más limpio de cada subtítulo) sobre las diapositivas y transiciones;
   - usa el audio original, con un fundido de salida de 1 s.
8. **Intro y cierre:** la intro original se sustituye por la de Sensation y el cierre original (cortinillas del curso) se elimina. La autoría queda en la intro y el cierre de Sensation: «Contenido original de John C. Maxwell».
9. **Render:** `scripts/render.sh <id>` y después QC: `ai/qc_composite.py` por tramo y revisión de fotogramas en cada plano, diapositiva y transición.
