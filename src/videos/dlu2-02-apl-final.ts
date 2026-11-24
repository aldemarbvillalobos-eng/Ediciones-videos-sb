import { Edit } from "../engine/types";

// DLU2_02_APL — VERSIÓN FINAL con la identidad aprobada (estudio Sensation + rótulos + diapositivas reconstruidas).
// Fuente: máster ensamblado por ai/assemble_master.py = contenido del original 6,9–119,5 s con la MISMA línea de tiempo
// (audio original). Se eliminaron la intro original (0–6,9 s) y el cierre original (119,5–128,9 s: cortinillas
// "Developing the Leader Within You" / "Application Two") para no duplicar intro y cierre.
// Tiempos relativos al máster (0 = 6,9 s del original).
export const dlu202aplFinal: Edit = {
  src: "procesados/dlu2-02-apl/master_estudio.mp4",
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
  watermarkRange: [1.2, 112.6],
  segments: [{ start: 0, end: 112.6 }],
  overlays: [
    // Rótulo original 7,55–12,2 s (x 164–650, y 885–1035): el nuevo ocupa la misma zona y tramo. Texto exacto del original.
    { type: "lowerThird", at: 0.62, dur: 4.75, name: "TRACI MORROW", role: "BUSINESS OWNER · ENTREPRENEUR", side: "left", x: 150, y: 878 },
  ],
  captions: [],
};
