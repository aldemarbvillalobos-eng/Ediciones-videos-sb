import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Identidad visual Sensation Academy (referencia corporativa del cliente).
// Logo oficial descargado de sensationacademy.net (wordmark "Sensation Brands").
// Jost (Google Fonts, OFL) empaquetada localmente: render sin dependencia de red.
export const fontFamily = "Jost";
loadFont({ family: fontFamily, url: staticFile("brand/fonts/Jost-latin.woff2"), weight: "300 700",
  unicodeRange: "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD" });
loadFont({ family: fontFamily, url: staticFile("brand/fonts/Jost-latin-ext.woff2"), weight: "300 700",
  unicodeRange: "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF" });

export const C = {
  purple: "#4B1D73",
  purple2: "#6A3FA0",
  gold: "#A87B05",
  beige: "#C5AE8A",
  white: "#FFFFFF",
  ink: "#1E0B30", // morado muy oscuro derivado para fondos/sombras
} as const;

export const EASE = [0.16, 1, 0.3, 1] as const; // ease-out elegante

export const SITE = "sensationacademy.net";
export const TAGLINE = "Aprende. Crece. Brilla.";
