import type { Caption } from "@remotion/captions";
import { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { C, fontFamily } from "./tokens";
import { useLayout } from "./useLayout";

type Page = { startMs: number; endMs: number; words: Caption[] };

const norm = (s: string) =>
  s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9ñ%]/g, "");

/** Agrupa palabras en páginas legibles: máx. caracteres por línea, 2 líneas, corta en pausas y puntuación. */
export const paginate = (caps: Caption[], maxChars: number): Page[] => {
  const pages: Page[] = [];
  let cur: Caption[] = [];
  let chars = 0;
  const flush = () => {
    if (cur.length) pages.push({ startMs: cur[0].startMs, endMs: cur[cur.length - 1].endMs, words: cur });
    cur = [];
    chars = 0;
  };
  caps.forEach((w, i) => {
    const prev = caps[i - 1];
    const gap = prev ? w.startMs - prev.endMs : 0;
    const t = w.text.trim();
    if (cur.length && (gap > 600 || chars + t.length + 1 > maxChars * 2)) flush();
    cur.push(w);
    chars += t.length + 1;
    if (/[.!?¿¡]$/.test(t) && chars > maxChars * 0.6) flush();
    else if (/[,;:]$/.test(t) && chars > maxChars * 1.3) flush();
  });
  flush();
  // mantener visible hasta la siguiente página si el hueco es corto
  pages.forEach((p, i) => {
    const n = pages[i + 1];
    p.endMs = n && n.startMs - p.endMs < 700 ? n.startMs : p.endMs + 250;
  });
  return pages;
};

/**
 * Subtítulos corporativos sincronizados palabra a palabra.
 * captions: tiempos relativos al ARCHIVO ORIGINAL. sourceOffsetMs: tiempo de origen que corresponde al frame 0 de este bloque.
 * keywords: palabras a destacar en dorado/beige.
 */
export const BrandCaptions: React.FC<{
  captions: Caption[];
  sourceOffsetMs: number;
  keywords?: string[];
  position?: "bottom" | "top";
}> = ({ captions, sourceOffsetMs, keywords = [], position = "bottom" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { u, vertical, width, safeY, height } = useLayout();
  const maxChars = vertical ? 22 : 38;
  const pages = useMemo(() => paginate(captions, maxChars), [captions, maxChars]);
  const kw = useMemo(() => new Set(keywords.flatMap((k) => k.split(" ")).map(norm)), [keywords]);
  const t = sourceOffsetMs + (frame / fps) * 1000;
  const page = pages.find((p) => t >= p.startMs && t < p.endMs);
  if (!page) return null;
  const local = t - page.startMs;
  const appear = interpolate(local, [0, 180], [0, 1], { extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const fade = interpolate(page.endMs - t, [0, 140], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fs = (vertical ? 58 : 50) * u;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        ...(position === "bottom" ? { bottom: vertical ? height * 0.2 : safeY * 1.1 } : { top: safeY * 1.2 }),
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(appear, fade),
        translate: `0 ${(1 - appear) * 14 * u}px`,
      }}
    >
      <div
        style={{
          maxWidth: width * (vertical ? 0.86 : 0.72),
          textAlign: "center",
          fontFamily,
          fontSize: fs,
          fontWeight: 600,
          lineHeight: 1.28,
          color: C.white,
          background: "rgba(30,11,48,0.62)",
          padding: `${10 * u}px ${26 * u}px ${12 * u}px`,
          borderRadius: 14 * u,
          boxDecorationBreak: "clone",
          textShadow: "0 2px 8px rgba(0,0,0,0.35)",
        }}
      >
        {page.words.map((w, i) => {
          const isKw = kw.has(norm(w.text));
          const spoken = t >= w.startMs;
          const hi = interpolate(t - w.startMs, [0, 120], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <span key={i}>
            {i > 0 ? " " : ""}
            <span
              style={{
                color: isKw ? (spoken ? C.beige : C.white) : C.white,
                opacity: spoken ? 1 : 0.72,
                ...(isKw
                  ? { backgroundImage: `linear-gradient(${C.gold}, ${C.gold})`, backgroundRepeat: "no-repeat", backgroundPosition: "0 92%", backgroundSize: `${hi * 100}% ${5 * u}px` }
                  : {}),
              }}
            >
              {w.text.trim()}
            </span>
            </span>
          );
        })}
      </div>
    </div>
  );
};
