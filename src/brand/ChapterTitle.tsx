import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily } from "./tokens";
import { inOut, prog } from "./anim";
import { useLayout } from "./useLayout";

/** Separador de tema sobre el video (banda elegante en el tercio superior/izquierdo). */
export const ChapterTitle: React.FC<{ index?: number; title: string }> = ({ index, title }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, safeX, safeY, vertical } = useLayout();
  const o = inOut(f, d, 16, 14);
  const p = prog(f, 0, 22);
  return (
    <div style={{ position: "absolute", left: safeX, top: vertical ? safeY * 1.3 : safeY * 1.2, opacity: o, fontFamily }}>
      {index !== undefined ? (
        <div style={{ color: C.gold, fontSize: 26 * u, fontWeight: 600, letterSpacing: 6 * u, textShadow: "0 2px 10px rgba(0,0,0,0.5)" }}>
          {String(index).padStart(2, "0")} · TEMA
        </div>
      ) : null}
      <div
        style={{
          marginTop: 10 * u,
          display: "inline-block",
          background: `linear-gradient(90deg, ${C.purple}F2, ${C.purple2}E6)`,
          color: C.white,
          fontSize: (vertical ? 52 : 50) * u,
          fontWeight: 600,
          padding: `${14 * u}px ${30 * u}px`,
          borderLeft: `${6 * u}px solid ${C.gold}`,
          clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
          maxWidth: (vertical ? 880 : 1100) * u,
          lineHeight: 1.15,
        }}
      >
        {title}
      </div>
    </div>
  );
};
