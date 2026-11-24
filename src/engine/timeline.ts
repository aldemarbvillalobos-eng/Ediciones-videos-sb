import { Edit, INTRO_S, OUTRO_S, OVERLAP_F } from "./types";

export const buildTimeline = (e: Edit) => {
  const { fps } = e;
  const introF = e.intro === false ? 0 : Math.round(INTRO_S * fps);
  const outroF = e.outro === false ? 0 : Math.round(OUTRO_S * fps);
  const bodyStart = introF ? introF - OVERLAP_F : 0;
  let cursor = bodyStart;
  const segs = e.segments.map((s) => {
    const trimBefore = Math.round(s.start * fps);
    const len = Math.max(1, Math.round(s.end * fps) - trimBefore);
    const item = { ...s, from: cursor, len, trimBefore };
    cursor += len;
    return item;
  });
  const bodyEnd = cursor;
  const outroFrom = outroF ? bodyEnd - OVERLAP_F : bodyEnd;
  const total = outroF ? outroFrom + outroF : bodyEnd;
  /** tiempo fuente (s) → frame de salida; null si fue recortado */
  const srcToOut = (t: number) => {
    for (const s of segs) {
      if (t >= s.start - 1e-3 && t < s.end) return s.from + Math.round((t - s.start) * fps);
    }
    // si cae en un hueco recortado, ir al siguiente segmento
    const next = segs.find((s) => s.start >= t);
    return next ? next.from : null;
  };
  return { introF, outroF, bodyStart, bodyEnd, outroFrom, total, segs, srcToOut };
};
