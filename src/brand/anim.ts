import { Easing, interpolate } from "remotion";
import { EASE } from "./tokens";

const ease = Easing.bezier(...EASE);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** 0→1 de entrada, 1→0 de salida, en frames locales. */
export const inOut = (frame: number, dur: number, inF = 15, outF = 12) =>
  Math.min(
    interpolate(frame, [0, inF], [0, 1], { ...clamp, easing: ease }),
    interpolate(frame, [dur - outF, dur], [1, 0], { ...clamp, easing: Easing.in(Easing.cubic) }),
  );

export const prog = (frame: number, a: number, b: number) =>
  interpolate(frame, [a, b], [0, 1], { ...clamp, easing: ease });
