import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "./tokens";

/** Transición corporativa: dos paneles (morado + filo dorado) cruzan la pantalla.
 *  Colocar centrada en el punto de corte (duración típica 18-22 frames). */
export const BrandWipe: React.FC = () => {
  const f = useCurrentFrame();
  const { durationInFrames: d } = useVideoConfig();
  const e = Easing.bezier(0.65, 0, 0.35, 1);
  const x = interpolate(f, [0, d], [-110, 110], { easing: e, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ translate: `${x - 6}% 0`, background: C.gold, transform: "skewX(-12deg) scaleX(1.3)" }} />
      <AbsoluteFill style={{ translate: `${x}% 0`, background: `linear-gradient(90deg, ${C.purple}, ${C.purple2})`, transform: "skewX(-12deg) scaleX(1.3)" }} />
    </AbsoluteFill>
  );
};
