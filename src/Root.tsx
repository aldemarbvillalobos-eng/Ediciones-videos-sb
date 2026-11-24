import { Composition, Folder } from "remotion";
import { EditedVideo } from "./engine/EditedVideo";
import { buildTimeline } from "./engine/timeline";
import { plantilla } from "./videos/_plantilla";
import { dlu202apl, dlu202aplMuestra } from "./videos/dlu2-02-apl";

// Registrar cada video editado como un <Composition> dentro de la carpeta "Entregas".
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Entregas">
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
