import { useCurrentFrame, useVideoConfig } from "remotion";
import { C, fontFamily } from "./tokens";
import { inOut, prog } from "./anim";
import { useLayout } from "./useLayout";
import { Icon, IconName } from "./Icons";

/** Tarjeta informativa / concepto clave. Se ubica en el lado libre del encuadre. */
export const InfoCard: React.FC<{
  title: string;
  points?: string[];
  icon?: IconName;
  side?: "left" | "right";
  kicker?: string;
}> = ({ title, points = [], icon, side = "right", kicker }) => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const { u, safeX, safeY, vertical, width } = useLayout();
  const o = inOut(f, d, 18, 14);
  const p = prog(f, 0, 20);
  const w = vertical ? width - safeX * 2 : 620 * u;
  return (
    <div
      style={{
        position: "absolute",
        ...(vertical ? { left: safeX, top: safeY * 1.4 } : { [side]: safeX, top: "50%", translate: `${(1 - p) * (side === "right" ? 40 : -40) * u}px -50%` }),
        width: w,
        opacity: o,
        fontFamily,
        background: "rgba(255,255,255,0.96)",
        borderRadius: 18 * u,
        overflow: "hidden",
        boxShadow: "0 24px 60px rgba(30,11,48,0.35)",
      }}
    >
      <div style={{ height: 6 * u, background: `linear-gradient(90deg, ${C.purple}, ${C.purple2} 60%, ${C.gold})`, width: `${p * 100}%` }} />
      <div style={{ padding: `${30 * u}px ${36 * u}px ${34 * u}px` }}>
        {kicker ? (
          <div style={{ color: C.gold, fontWeight: 600, fontSize: 22 * u, letterSpacing: 4 * u, textTransform: "uppercase", marginBottom: 10 * u }}>{kicker}</div>
        ) : null}
        <div style={{ display: "flex", alignItems: "center", gap: 18 * u }}>
          {icon ? (
            <div style={{ flex: "none", width: 64 * u, height: 64 * u, borderRadius: 16 * u, background: C.purple, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Icon name={icon} size={36 * u} color={C.white} progress={prog(f, 6, 30)} />
            </div>
          ) : null}
          <div style={{ color: C.purple, fontSize: 40 * u, fontWeight: 700, lineHeight: 1.12 }}>{title}</div>
        </div>
        {points.length ? (
          <div style={{ marginTop: 20 * u, display: "flex", flexDirection: "column", gap: 12 * u }}>
            {points.map((pt, i) => {
              const s = prog(f, 14 + i * 8, 32 + i * 8);
              return (
                <div key={i} style={{ display: "flex", gap: 14 * u, alignItems: "baseline", opacity: s, translate: `${(1 - s) * 16 * u}px 0` }}>
                  <div style={{ flex: "none", width: 10 * u, height: 10 * u, borderRadius: 2 * u, rotate: "45deg", background: C.gold, translate: `0 ${-3 * u}px` }} />
                  <div style={{ color: "#2B2233", fontSize: 30 * u, fontWeight: 400, lineHeight: 1.3 }}>{pt}</div>
                </div>
              );
            })}
          </div>
        ) : null}
      </div>
    </div>
  );
};
