import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily, SITE, TAGLINE } from "./tokens";
import { inOut, prog } from "./anim";
import { useLayout } from "./useLayout";

/** Cierre corporativo (~4.5 s). */
export const Outro: React.FC<{ cta?: string; credit?: string }> = ({ cta, credit }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, vertical } = useLayout();
  const o = inOut(f, d, 14, 18);
  const a = prog(f, 6, 30);
  const b = prog(f, 18, 42);
  const c = prog(f, 28, 52);
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        background: `linear-gradient(160deg, ${C.purple} 0%, ${C.ink} 100%)`,
        alignItems: "center",
        justifyContent: "center",
        fontFamily,
        color: C.white,
        textAlign: "center",
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 26 * u }}>
        <Img src={staticFile("brand/logo-sensation-blanco.png")} style={{ width: (vertical ? 560 : 480) * u, opacity: a, scale: `${0.94 + 0.06 * a}` }} />
        <div style={{ fontSize: 40 * u, fontWeight: 500, opacity: b, translate: `0 ${(1 - b) * 16 * u}px` }}>{cta ?? TAGLINE}</div>
        <div style={{ width: 300 * u * b, height: 3 * u, background: C.gold }} />
        <div
          style={{
            opacity: c,
            fontSize: 34 * u,
            fontWeight: 600,
            letterSpacing: 2 * u,
            padding: `${14 * u}px ${38 * u}px`,
            border: `${2 * u}px solid ${C.beige}`,
            borderRadius: 999,
            color: C.white,
          }}
        >
          {SITE}
        </div>
        {credit ? <div style={{ opacity: c * 0.7, fontSize: 22 * u, fontWeight: 300, marginTop: 10 * u }}>{credit}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
