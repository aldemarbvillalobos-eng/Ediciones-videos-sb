import { useVideoConfig } from "remotion";

// Escala tipográfica y márgenes seguros según resolución/orientación.
export const useLayout = () => {
  const { width, height } = useVideoConfig();
  const vertical = height > width;
  const base = Math.min(width, height); // 1080 en FullHD horizontal o vertical
  const u = base / 1080;
  return {
    width,
    height,
    vertical,
    u,
    safeX: (vertical ? 70 : 110) * u,
    safeY: (vertical ? 160 : 70) * u,
  };
};
