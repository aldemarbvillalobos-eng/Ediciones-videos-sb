import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily } from "./tokens";
import { inOut, prog } from "./anim";
import { useLayout } from "./useLayout";

/** Nombre y cargo del presentador. side: lado libre del encuadre (no cubrir rostro). */
/** x/y opcionales: posición exacta en px (p. ej. para cubrir un rótulo original en la misma zona). */
export const LowerThird: React.FC<{ name: string; role?: string; side?: "left" | "right"; x?: number; y?: number }> = ({ name, role, side = "left", x, y }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, safeX, vertical, height } = useLayout();
  const o = inOut(f, d, 18, 14);
  const bar = prog(f, 0, 16);
  const t = prog(f, 8, 26);
  return (
    <div
      style={{
        position: "absolute",
        [side]: x ?? safeX,
        top: y ?? (vertical ? height * 0.6 : height * 0.62),
        opacity: o,
        fontFamily,
        display: "flex",
        alignItems: "stretch",
        gap: 18 * u,
        flexDirection: side === "left" ? "row" : "row-reverse",
        textAlign: side,
      }}
    >
      <div style={{ width: 6 * u, background: C.gold, borderRadius: 3, scale: `1 ${bar}` }} />
      <div
        style={{
          background: `linear-gradient(90deg, ${C.purple}, ${C.purple2})`, // opaco: cubre por completo la zona del rótulo original
          padding: `${16 * u}px ${30 * u}px`,
          borderRadius: 10 * u,
          clipPath: `inset(0 ${(1 - bar) * 100}% 0 0)`,
          boxShadow: "0 10px 30px rgba(0,0,0,0.25)",
        }}
      >
        <div style={{ color: C.white, fontSize: 40 * u, fontWeight: 600, opacity: t, lineHeight: 1.15 }}>{name}</div>
        {role ? <div style={{ color: C.beige, fontSize: 26 * u, fontWeight: 400, opacity: t, marginTop: 4 * u, letterSpacing: 0.5 * u }}>{role}</div> : null}
      </div>
    </div>
  );
};
