import { Edit } from "../engine/types";

// DLU2_02_APL — "Desarrolle el líder que está en usted", Aplicación dos: La clave del liderazgo: Prioridades.
// Contenido original de John C. Maxwell (licenciado). Adaptación corporativa: sin cortes, sin subtítulos nuevos
// (se conservan los subtítulos en español incrustados), sin gráficos sobre el contenido original.
// Audio y video originales intactos (copia sin recodificar; audio −19 LUFS, bien mezclado).

// Intro original sustituida por la de Sensation Academy (licencia lo permite). Análisis del original:
//  - título "Application Two" hasta 5,0 s, fundido a negro 5,0–6,2 s, negro 6,2–6,6 s
//  - música de la intro termina en 6,06 s (silencio total 6,06–6,66 s)
//  - presentadora aparece en fundido desde 6,7 s; primera palabra a los 7,66 s
// Se empieza en 6,9 s: sin restos de la intro original y sin recortar la primera frase.
const CONTENT_START = 6.9;

const base: Omit<Edit, "segments"> = {
  src: "procesados/dlu2-02-apl/original.mp4",
  fps: 30,
  width: 1920,
  height: 1080,
  intro: {
    kicker: "Desarrolle el líder que está en usted",
    title: "La clave del liderazgo: Prioridades",
    subtitle: "Lección 2 · Aplicación dos",
    credit: "Contenido original de John C. Maxwell",
  },
  outro: { credit: "Desarrolle el líder que está en usted · Contenido original de John C. Maxwell" },
  watermark: true,
  introTransitionF: 20, // fundido cruzado de 0,67 s entre nuestra intro y la presentadora
  // entre la cortinilla inicial y la final del curso (no se superpone a los títulos originales)
  watermarkRange: [8, 107.3],
  overlays: [],
  captions: [],
};

/** Edición completa (2:09 + intro + cierre). */
export const dlu202apl: Edit = { ...base, segments: [{ start: CONTENT_START, end: 128.9 }] };

/** Muestra de revisión (~50 s): intro + primeros 43 s (cierra al final de frase) + cierre. */
export const dlu202aplMuestra: Edit = { ...base, segments: [{ start: CONTENT_START, end: 43.1 }] };
