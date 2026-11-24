import { Composition, Folder } from "remotion";
import { EditedVideo } from "./engine/EditedVideo";
import { buildTimeline } from "./engine/timeline";
import { plantilla } from "./videos/_plantilla";

// Registrar cada video editado como un <Composition> dentro de la carpeta "Entregas".
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="Entregas">{/* videos editados aquí */}</Folder>
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
