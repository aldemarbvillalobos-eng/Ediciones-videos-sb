import { colorCorrection } from "@remotion/effects/color-correction";
import { Audio, Video } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrandCaptions } from "../brand/Captions";
import { BrandWipe } from "../brand/BrandWipe";
import { ChapterTitle } from "../brand/ChapterTitle";
import { InfoCard } from "../brand/InfoCard";
import { Intro } from "../brand/Intro";
import { LowerThird } from "../brand/LowerThird";
import { Outro } from "../brand/Outro";
import { Watermark } from "../brand/Watermark";
import { C } from "../brand/tokens";
import { buildTimeline } from "./timeline";
import { Edit, Segment } from "./types";

const ZoomFrame: React.FC<{ seg: Segment; len: number; children: React.ReactNode }> = ({ seg, len, children }) => {
  const f = useCurrentFrame();
  const z = seg.zoom ?? 1;
  const p = seg.pushIn ?? 0;
  const [fx, fy] = seg.focus ?? [0.5, 0.4];
  const s = z + p * interpolate(f, [0, len], [0, 1], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ scale: `${s}`, transformOrigin: `${fx * 100}% ${fy * 100}%` }}>{children}</AbsoluteFill>;
};

export const EditedVideo: React.FC<{ edit: Edit }> = ({ edit }) => {
  const { fps } = useVideoConfig();
  const tl = buildTimeline(edit);
  const fx = edit.color ? [colorCorrection(edit.color)] : [];
  const fadeF = 2; // micro-fundido de audio en cada corte (evita clics)
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {tl.segs.map((s, i) => (
        <Sequence key={i} name={`Corte ${i + 1} (${s.start.toFixed(2)}–${s.end.toFixed(2)} s)`} from={s.from} durationInFrames={s.len}>
          <ZoomFrame seg={s} len={s.len}>
            <Video
              src={staticFile(edit.src)}
              trimBefore={s.trimBefore}
              effects={fx}
              style={{ width: "100%", height: "100%" }}
              objectFit="cover"
              volume={(f) =>
                Math.min(
                  interpolate(f, [0, fadeF], [0, 1], { extrapolateRight: "clamp" }),
                  interpolate(f, [s.len - fadeF, s.len], [1, 0], { extrapolateLeft: "clamp" }),
                )
              }
            />
          </ZoomFrame>
          <BrandCaptions captions={edit.captions} sourceOffsetMs={s.start * 1000} keywords={edit.keywords} position={edit.captionsPosition} />
        </Sequence>
      ))}

      {edit.overlays.map((o, i) => {
        const from = tl.srcToOut(o.at);
        if (from === null) return null;
        const d = Math.round(o.dur * fps);
        return (
          <Sequence key={`o${i}`} name={`${o.type}: ${"title" in o ? o.title : o.name}`} from={from} durationInFrames={d} layout="none">
            <AbsoluteFill>
              {o.type === "lowerThird" ? <LowerThird name={o.name} role={o.role} side={o.side} /> : null}
              {o.type === "card" ? <InfoCard title={o.title} points={o.points} icon={o.icon} side={o.side} kicker={o.kicker} /> : null}
              {o.type === "chapter" ? <ChapterTitle index={o.index} title={o.title} /> : null}
            </AbsoluteFill>
          </Sequence>
        );
      })}

      {edit.watermark !== false ? (
        <Sequence name="Marca de agua" from={tl.bodyStart + 20} durationInFrames={tl.outroFrom - tl.bodyStart - 20}>
          <Watermark />
        </Sequence>
      ) : null}

      {tl.segs.map((s, i) =>
        s.wipeBefore && i > 0 ? (
          <Sequence key={`w${i}`} name="Transición" from={s.from - 10} durationInFrames={20}>
            <BrandWipe />
          </Sequence>
        ) : null,
      )}

      {tl.introF ? (
        <Sequence name="Intro" durationInFrames={tl.introF}>
          <Intro {...(edit.intro || {})} />
        </Sequence>
      ) : null}
      {tl.outroF ? (
        <Sequence name="Cierre" from={tl.outroFrom} durationInFrames={tl.outroF}>
          <Outro {...(edit.outro || {})} />
        </Sequence>
      ) : null}

      {edit.music ? (
        <Audio
          name="Música"
          src={staticFile(edit.music.src)}
          trimBefore={Math.round((edit.music.startAt ?? 0) * fps)}
          loop
          volume={(f) =>
            edit.music!.volume *
            Math.min(
              interpolate(f, [0, fps], [0, 1], { extrapolateRight: "clamp" }),
              interpolate(f, [tl.total - 2 * fps, tl.total], [1, 0], { extrapolateLeft: "clamp" }),
            ) *
            // más presente en intro/cierre, discreta bajo la voz
            (f < tl.bodyStart + 10 || f > tl.outroFrom ? 2.2 : 1)
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};
