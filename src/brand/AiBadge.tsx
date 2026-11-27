import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily } from "./tokens";
import { inOut } from "./anim";
import { useLayout } from "./useLayout";

/** Aviso discreto de transparencia: el video es una adaptación audiovisual con IA. */
export const AiBadge: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, safeX, safeY } = useLayout();
  return (
    <div
      style={{
        position: "absolute",
        left: safeX * 0.7,
        top: safeY * 0.8,
        opacity: 0.85 * inOut(f, d, 20, 20),
        fontFamily,
        display: "flex",
        alignItems: "center",
        gap: 10 * u,
        padding: `${7 * u}px ${16 * u}px`,
        borderRadius: 999,
        background: "rgba(30,11,48,0.55)",
        border: `${1.5 * u}px solid ${C.gold}99`,
        color: C.white,
        fontSize: 20 * u,
        fontWeight: 500,
        letterSpacing: 1 * u,
      }}
    >
      <div style={{ width: 8 * u, height: 8 * u, borderRadius: 4 * u, background: C.gold }} />
      {text}
    </div>
  );
};
