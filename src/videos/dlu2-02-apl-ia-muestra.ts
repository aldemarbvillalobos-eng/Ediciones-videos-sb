import { Edit } from "../engine/types";

// PRUEBA — DLU2_02_APL con presentadora virtual (IA). Fragmento de 15 s: original 75,0–90,0 s
// (plano medio → primer plano → plano medio). Fuente: ai/lp_composite.py sobre el máster de estudio aprobado.
// Voz, subtítulos, cuerpo y escenario: originales/aprobados. Cabeza: presentadora virtual animada con la actuación original.
export const dlu202aplIaMuestra: Edit = {
  src: "procesados/dlu2-02-apl/ia_muestra.mp4",
  fps: 30,
  width: 1920,
  height: 1080,
  intro: false,
  outro: false,
  watermark: true,
  segments: [{ start: 0, end: 15.0 }],
  overlays: [
    // Aviso de IA con el crédito de la voz original (no se atribuye el nombre de la presentadora original a la virtual).
    { type: "badge", at: 0, dur: 15.0, text: "Adaptación audiovisual con IA · Voz original: Traci Morrow" },
    // Rótulo: identifica a la presentadora virtual como tal.
    { type: "lowerThird", at: 0.4, dur: 5.0, name: "PRESENTADORA VIRTUAL (IA)", role: "SENSATION ACADEMY", side: "left", x: 110, y: 640 },
  ],
  captions: [],
};
