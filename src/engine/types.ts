import type { Caption } from "@remotion/captions";
import type { IconName } from "../brand/Icons";

/** Todos los tiempos en SEGUNDOS del archivo original (fuente). */
export type Segment = {
  start: number;
  end: number;
  /** escala base (1 = encuadre original). Alternar 1 / 1.08 disimula cortes. */
  zoom?: number;
  /** acercamiento lento durante el segmento (p. ej. 0.04) */
  pushIn?: number;
  /** punto focal 0-1 (rostro) para los zooms */
  focus?: [number, number];
  /** transición corporativa antes de este segmento */
  wipeBefore?: boolean;
};

export type Overlay =
  | { type: "lowerThird"; at: number; dur: number; name: string; role?: string; side?: "left" | "right"; x?: number; y?: number }
  | { type: "card"; at: number; dur: number; title: string; points?: string[]; icon?: IconName; side?: "left" | "right"; kicker?: string }
  | { type: "chapter"; at: number; dur: number; index?: number; title: string };

export type ColorFix = {
  exposure?: number;
  temperature?: number;
  tint?: number;
  shadows?: number;
  highlights?: number;
  contrast?: number;
  saturation?: number;
  vibrance?: number;
};

export type Edit = {
  /** ruta dentro de public/ del video de trabajo (audio mejorado) */
  src: string;
  fps: number;
  width: number;
  height: number;
  intro?: { title?: string; subtitle?: string; kicker?: string; credit?: string } | false;
  outro?: { cta?: string; credit?: string } | false;
  /** tramo de salida (s, tiempo fuente) donde se muestra la marca de agua */
  watermarkRange?: [number, number];
  watermark?: boolean;
  /** duración (frames) del fundido intro → contenido; por defecto OVERLAP_F */
  introTransitionF?: number;
  color?: ColorFix;
  music?: { src: string; volume: number; startAt?: number };
  keywords?: string[];
  captionsPosition?: "bottom" | "top";
  segments: Segment[];
  overlays: Overlay[];
  captions: Caption[];
};

export const INTRO_S = 4.4;
export const OUTRO_S = 4.6;
export const OVERLAP_F = 12;
