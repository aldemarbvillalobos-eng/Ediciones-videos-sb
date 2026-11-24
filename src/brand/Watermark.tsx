import { Img, staticFile } from "remotion";
import { useLayout } from "./useLayout";

/** Marca de agua discreta (esquina superior derecha). */
export const Watermark: React.FC<{ opacity?: number }> = ({ opacity = 0.55 }) => {
  const { u, safeX, safeY, vertical } = useLayout();
  return (
    <Img
      src={staticFile("brand/logo-sensation-blanco.png")}
      style={{
        position: "absolute",
        top: (vertical ? safeY * 0.6 : safeY * 0.8),
        right: safeX * 0.7,
        width: 170 * u,
        opacity,
        filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.45))",
      }}
    />
  );
};
