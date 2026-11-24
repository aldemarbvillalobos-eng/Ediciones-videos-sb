import { Edit } from "../engine/types";

// PLANTILLA de referencia: copiar a src/videos/<slug>.ts y adaptar. No se registra en Root.
const words = "Bienvenidos a esta capacitación de Sensation Academy. Hoy aprenderemos tres claves del liderazgo efectivo: comunicación, confianza y propósito. Empecemos.".split(" ");
export const plantilla: Edit = {
  src: "procesados/_demo/source.mp4",
  fps: 30,
  width: 1920,
  height: 1080,
  intro: { title: "Liderazgo efectivo", subtitle: "Módulo 1 · Fundamentos" },
  outro: {},
  watermark: true,
  color: { exposure: 0.15, contrast: 1.05, vibrance: 0.1 },
  keywords: ["liderazgo", "comunicación", "confianza", "propósito"],
  segments: [
    { start: 0.5, end: 6, zoom: 1, pushIn: 0.03, focus: [0.5, 0.4] },
    { start: 7, end: 12, zoom: 1.08, focus: [0.5, 0.4] },
    { start: 12.5, end: 19, zoom: 1, wipeBefore: true },
  ],
  overlays: [
    { type: "lowerThird", at: 1, dur: 4.5, name: "Nombre Presentador", role: "Facilitador · Sensation Academy", side: "left" },
    { type: "card", at: 7.5, dur: 4, title: "3 claves del liderazgo", points: ["Comunicación", "Confianza", "Propósito"], icon: "target", side: "right", kicker: "Concepto clave" },
    { type: "chapter", at: 12.6, dur: 3, index: 1, title: "Comunicación" },
  ],
  captions: words.map((w, i) => ({ text: (i ? " " : "") + w, startMs: 600 + i * 780, endMs: 600 + i * 780 + 700, timestampMs: null, confidence: null })),
};
