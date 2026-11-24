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
- Audio y video originales sin reprocesar: copia sin recodificar a `public/procesados/<slug>/original.mp4`.
- Muestra aprobada pendiente: `dlu2-02-apl-muestra`. Si se aprueba, renderizar `dlu2-02-apl` (completo).
- DLU2_01_LEC.mp4 (md5 2f85592e…): 83 paquetes H.264 inválidos entre 1192,3 y 1195,0 s (no recuperables) y ningún dato de video después de 1195 s (el audio sigue hasta 1709 s). Queda en espera de una copia íntegra.
