// Instala whisper.cpp (CPU) y descarga el modelo multilingüe para español.
import path from "node:path";
import { installWhisperCpp, downloadWhisperModel } from "@remotion/install-whisper-cpp";

const to = path.join(process.cwd(), "whisper.cpp");
const model = process.argv[2] ?? "large-v3-turbo";
await installWhisperCpp({ to, version: "1.7.6", printOutput: true });
await downloadWhisperModel({ model, folder: to, printOutput: true });
console.log("Whisper listo:", model);
