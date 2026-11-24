import { Edit } from "../engine/types";

// PRUEBA AVANZADA — DLU2_02_APL, fragmento 6,9–33,0 s del original (26,1 s).
// La fuente es el fragmento ya compuesto en Python (ai/composite_bg.py):
// presentadora original + fondo de estudio Sensation, con el rótulo original eliminado y los subtítulos protegidos.
// Aquí se añaden la intro, el rótulo rediseñado (mismo nombre y cargo que el original), el logo y el cierre.
// Los tiempos son relativos al fragmento (0 = 6,9 s del original).
export const dlu202aplEstudio: Edit = {
  src: "procesados/dlu2-02-apl/fragmento_estudio.mp4",
  fps: 30,
  width: 1920,
  height: 1080,
  intro: {
    kicker: "Desarrolle el líder que está en usted",
    title: "La clave del liderazgo: Prioridades",
    subtitle: "Lección 2 · Aplicación dos",
    credit: "Contenido original de John C. Maxwell",
  },
  introTransitionF: 20,
  outro: { credit: "Desarrolle el líder que está en usted · Contenido original de John C. Maxwell" },
  watermark: true,
  watermarkRange: [1.2, 26.0],
  segments: [{ start: 0, end: 26.1 }],
  overlays: [
    // Rótulo original 7,55–12,2 s (x 164–650, y 885–1035): el nuevo se coloca en la MISMA zona y tramo y la cubre;
    // mismo texto que el original (OCR verificado visualmente).
    { type: "lowerThird", at: 0.62, dur: 4.75, name: "TRACI MORROW", role: "BUSINESS OWNER · ENTREPRENEUR", side: "left", x: 150, y: 878 },
  ],
  captions: [],
};
