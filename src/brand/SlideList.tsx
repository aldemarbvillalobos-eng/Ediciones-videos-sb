import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily } from "./tokens";
import { prog } from "./anim";

/**
 * Diapositiva educativa (título + lista numerada) con la identidad Sensation.
 * Reconstruye una diapositiva original con su texto EXACTO y sus tiempos de aparición (en segundos, relativos al inicio).
 * La franja inferior (y > 840) queda libre para los subtítulos originales.
 */
export const SlideList: React.FC<{ title: string; titleAt: number; items: { text: string; at: number }[] }> = ({ title, titleAt, items }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (s: number) => Math.round(s * fps);
  const tIn = prog(f, t(titleAt), t(titleAt) + 22);
  const drift = interpolate(f, [0, 600], [0, 1]);
  const lastShown = items.filter((it) => f >= t(it.at)).length;
  const lineP = lastShown <= 1 ? 0 : prog(f, t(items[lastShown - 1].at), t(items[lastShown - 1].at) + 18);
  const lineTo = lastShown <= 1 ? 0 : (lastShown - 2 + lineP) / Math.max(1, items.length - 1);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(90% 80% at ${62 + drift * 3}% 30%, ${C.purple2} 0%, ${C.purple} 38%, ${C.ink} 100%)`, fontFamily }}>
      {/* profundidad: paneles y filos dorados desenfocados, como el set de estudio */}
      <AbsoluteFill style={{ filter: "blur(14px)", opacity: 0.55 }}>
        {[1500, 1640, 1780].map((x, i) => (
          <div key={x} style={{ position: "absolute", left: x, top: 80, width: 90, height: 900, background: `linear-gradient(180deg, ${C.purple2}55, transparent)`, borderRight: `3px solid ${C.gold}${i === 1 ? "AA" : "55"}` }} />
        ))}
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "radial-gradient(120% 100% at 50% 50%, transparent 55%, rgba(10,3,20,0.55) 100%)" }} />

      {/* Título */}
      <div style={{ position: "absolute", left: 150, top: 175, opacity: tIn, translate: `${(1 - tIn) * -30}px 0` }}>
        <div
          style={{
            color: C.white,
            fontSize: 66,
            fontWeight: 600,
            letterSpacing: 1,
            padding: "14px 34px 16px",
            background: `linear-gradient(90deg, ${C.purple}, ${C.purple2})`,
            borderLeft: `8px solid ${C.gold}`,
            clipPath: `inset(0 ${(1 - tIn) * 100}% 0 0)`,
            boxShadow: "0 18px 50px rgba(10,3,20,0.45)",
          }}
        >
          {title}
        </div>
      </div>

      {/* Línea de progresión (las preguntas se responden en orden) */}
      <div style={{ position: "absolute", left: 206, top: 432, width: 4, height: 300 * lineTo, background: `linear-gradient(180deg, ${C.gold}, ${C.beige})`, borderRadius: 2 }} />

      {items.map((it, i) => {
        const p = prog(f, t(it.at), t(it.at) + 20);
        const pop = interpolate(f, [t(it.at), t(it.at) + 14], [0.6, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(1.6)) });
        return (
          <div key={i} style={{ position: "absolute", left: 180, top: 400 + i * 150, display: "flex", alignItems: "center", gap: 34, opacity: p }}>
            <div
              style={{
                width: 60,
                height: 60,
                borderRadius: 30,
                background: C.gold,
                color: C.white,
                fontSize: 32,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                scale: `${pop}`,
                boxShadow: `0 0 0 6px ${C.gold}33`,
              }}
            >
              {it.text.match(/^(\d+)\./)?.[1]}
            </div>
            <div style={{ color: C.white, fontSize: 54, fontWeight: 500, translate: `${(1 - p) * 40}px 0`, textShadow: "0 3px 14px rgba(0,0,0,0.35)" }}>
              {it.text.replace(/^\d+\.\s*/, "")}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
