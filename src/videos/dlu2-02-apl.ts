import { Edit } from "../engine/types";

// DLU2_02_APL — "Desarrolle el líder que está en usted", Aplicación dos: La clave del liderazgo: Prioridades.
// Contenido original de John C. Maxwell (licenciado). Adaptación corporativa: sin cortes, sin subtítulos nuevos
// (se conservan los subtítulos en español incrustados), sin gráficos sobre el contenido original.
// Audio y video originales intactos (copia sin recodificar; audio −19 LUFS, bien mezclado).

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
  // entre la cortinilla inicial y la final del curso (no se superpone a los títulos originales)
  watermarkRange: [8, 107.3],
  overlays: [],
  captions: [],
};

/** Edición completa (2:09 + intro + cierre). */
export const dlu202apl: Edit = { ...base, segments: [{ start: 0, end: 128.9 }] };

/** Muestra de revisión (~50 s): intro + primeros 43 s (cierra al final de frase) + cierre. */
export const dlu202aplMuestra: Edit = { ...base, segments: [{ start: 0, end: 43.1 }] };
