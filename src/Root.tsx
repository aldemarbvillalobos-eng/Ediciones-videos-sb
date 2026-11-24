import { Composition, Folder } from "remotion";
import { EditedVideo } from "./engine/EditedVideo";
import { buildTimeline } from "./engine/timeline";
import { plantilla } from "./videos/_plantilla";
import { dlu202apl, dlu202aplMuestra } from "./videos/dlu2-02-apl";
import { dlu202aplEstudio } from "./videos/dlu2-02-apl-estudio";
import { dlu202aplFinal } from "./videos/dlu2-02-apl-final";
import { SlideList } from "./brand/SlideList";
import { Intro } from "./brand/Intro";
import { Outro } from "./brand/Outro";

// Registrar cada video editado como un <Composition> dentro de la carpeta "Entregas".
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Entregas">
        <Composition
          id="dlu2-02-apl-final"
          component={EditedVideo}
          fps={dlu202aplFinal.fps}
          width={dlu202aplFinal.width}
          height={dlu202aplFinal.height}
          durationInFrames={buildTimeline(dlu202aplFinal).total}
          defaultProps={{ edit: dlu202aplFinal }}
        />
        <Composition
          id="dlu2-02-apl-muestra"
          component={EditedVideo}
          fps={dlu202aplMuestra.fps}
          width={dlu202aplMuestra.width}
          height={dlu202aplMuestra.height}
          durationInFrames={buildTimeline(dlu202aplMuestra).total}
          defaultProps={{ edit: dlu202aplMuestra }}
        />
        <Composition
          id="dlu2-02-apl"
          component={EditedVideo}
          fps={dlu202apl.fps}
          width={dlu202apl.width}
          height={dlu202apl.height}
          durationInFrames={buildTimeline(dlu202apl).total}
          defaultProps={{ edit: dlu202apl }}
        />
        <Composition
          id="dlu2-02-apl-estudio-prueba"
          component={EditedVideo}
          fps={dlu202aplEstudio.fps}
          width={dlu202aplEstudio.width}
          height={dlu202aplEstudio.height}
          durationInFrames={buildTimeline(dlu202aplEstudio).total}
          defaultProps={{ edit: dlu202aplEstudio }}
        />
      </Folder>
      <Folder name="Intros">
        {/* DLU2_01_LEC: solo se sustituye la intro original (0–12,07 s). Texto según la cortinilla original
            «Section One · The Definition of Leadership & Influence» / «Sección uno · La definición de liderazgo e influencia». */}
        <Composition
          id="dlu2-01-lec-intro"
          component={Intro}
          fps={30}
          width={1920}
          height={1080}
          durationInFrames={132}
          defaultProps={{
            kicker: "Desarrolle el líder que está en usted",
            title: "La definición de liderazgo e influencia",
            subtitle: "Sección uno",
            credit: "Contenido original de John C. Maxwell",
            outFrames: 1,
          }}
        />
        {/* Cierre de Sensation que marca el final de DLU2_01_LEC (la imagen del archivo original llega hasta 1192 s). */}
        <Composition
          id="dlu2-01-lec-cierre"
          component={Outro}
          fps={30}
          width={1920}
          height={1080}
          durationInFrames={138}
          defaultProps={{ credit: "Desarrolle el líder que está en usted · Contenido original de John C. Maxwell" }}
        />
      </Folder>
      <Folder name="Diapositivas">
        {/* DLU2_02_APL «¿QUÉ ES MÁS IMPORTANTE?» — texto y tiempos exactos del original (OCR + revisión visual).
            Inicio = comienzo del destello original (54,87 s y 107,4 s); tiempos relativos a ese inicio. */}
        <Composition
          id="apl-diapositiva-1"
          component={SlideList}
          fps={30}
          width={1920}
          height={1080}
          durationInFrames={392}
          defaultProps={{
            title: "¿QUÉ ES MÁS IMPORTANTE?",
            titleAt: 1.06,
            items: [
              { text: "1. ¿Qué se requiere de mí?", at: 2.66 },
              { text: "2. ¿Qué me da el mayor resultado?", at: 5.9 },
              { text: "3. ¿Qué me brinda la máxima recompensa?", at: 8.63 },
            ],
          }}
        />
        <Composition
          id="apl-diapositiva-2"
          component={SlideList}
          fps={30}
          width={1920}
          height={1080}
          durationInFrames={363}
          defaultProps={{
            title: "¿QUÉ ES MÁS IMPORTANTE?",
            titleAt: 1.23,
            items: [
              { text: "1. ¿Qué se requiere de mí?", at: 2.7 },
              { text: "2. ¿Qué me da el mayor resultado?", at: 3.87 },
              { text: "3. ¿Qué me brinda la máxima recompensa?", at: 5.03 },
            ],
          }}
        />
      </Folder>
      <Folder name="Pruebas">
        {/* Requiere: scripts/demo-source.sh */}
        <Composition
          id="Plantilla"
          component={EditedVideo}
          fps={plantilla.fps}
          width={plantilla.width}
          height={plantilla.height}
          durationInFrames={buildTimeline(plantilla).total}
          defaultProps={{ edit: plantilla }}
        />
      </Folder>
    </>
  );
};
