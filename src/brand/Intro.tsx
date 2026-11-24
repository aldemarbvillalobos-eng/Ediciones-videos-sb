import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily, TAGLINE } from "./tokens";
import { inOut, prog } from "./anim";
import { useLayout } from "./useLayout";

/** Introducción corporativa breve (~3 s). Título opcional del video. */
export const Intro: React.FC<{ title?: string; subtitle?: string; kicker?: string; credit?: string; outFrames?: number }> = ({ title, subtitle, kicker, credit, outFrames = 14 }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, vertical } = useLayout();
  const o = inOut(f, d, 1, outFrames);
  const line = prog(f, 8, 30);
  const logo = prog(f, 4, 26);
  const txt = prog(f, 18, 40);
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        background: `radial-gradient(120% 90% at 50% 40%, ${C.purple2} 0%, ${C.purple} 45%, ${C.ink} 100%)`,
        alignItems: "center",
        justifyContent: "center",
        fontFamily,
        color: C.white,
      }}
    >
      {/* textura sutil: anillos dorados */}
      <AbsoluteFill style={{ opacity: 0.12 * logo }}>
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
          {[18, 28, 38, 48].map((r) => (
            <circle key={r} cx="50" cy="45" r={r * (0.9 + 0.1 * logo + 0.08 * (f / d))} fill="none" stroke={C.beige} strokeWidth={0.15} />
          ))}
        </svg>
      </AbsoluteFill>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 28 * u, scale: `${1 + 0.025 * (f / d)}` }}>
        <Img
          src={staticFile("brand/logo-sensation-blanco.png")}
          style={{ width: (vertical ? 620 : 560) * u, opacity: logo, translate: `0 ${(1 - logo) * 30 * u}px`, filter: `blur(${(1 - logo) * 8}px)` }}
        />
        <div style={{ width: 360 * u * line, height: 3 * u, background: C.gold, borderRadius: 2 }} />
        <div style={{ fontSize: 30 * u, letterSpacing: 10 * u, fontWeight: 500, textTransform: "uppercase", color: C.beige, opacity: txt }}>
          Sensation Academy
        </div>
        {title ? (
          <div style={{ opacity: txt, translate: `0 ${(1 - txt) * 20 * u}px`, textAlign: "center", maxWidth: (vertical ? 900 : 1400) * u }}>
            {kicker ? <div style={{ fontSize: 24 * u, fontWeight: 500, letterSpacing: 5 * u, textTransform: "uppercase", color: C.beige, marginTop: 10 * u }}>{kicker}</div> : null}
            <div style={{ fontSize: (vertical ? 64 : 60) * u, fontWeight: 600, lineHeight: 1.1, marginTop: 14 * u }}>{title}</div>
            {subtitle ? <div style={{ fontSize: 32 * u, fontWeight: 400, marginTop: 14 * u, opacity: 0.92 }}>{subtitle}</div> : null}
            {credit ? <div style={{ fontSize: 24 * u, fontWeight: 300, marginTop: 26 * u, opacity: 0.75, letterSpacing: 1 * u }}>{credit}</div> : null}
          </div>
        ) : (
          <div style={{ fontSize: 26 * u, fontWeight: 300, opacity: txt * 0.85, letterSpacing: 2 * u }}>{TAGLINE}</div>
        )}
      </div>
    </AbsoluteFill>
  );
};
