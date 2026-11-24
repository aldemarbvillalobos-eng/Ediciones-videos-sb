// Uso: node scripts/transcribe.mjs <slug> [modelo]
// Transcribe public/procesados/<slug>/audio16k.wav -> public/procesados/<slug>/captions.json (palabra a palabra)
import path from "node:path";
import fs from "node:fs";
import { transcribe, toCaptions } from "@remotion/install-whisper-cpp";

const slug = process.argv[2];
const model = process.argv[3] ?? "large-v3-turbo";
if (!slug) throw new Error("Falta el slug");
const dir = path.join(process.cwd(), "public", "procesados", slug);
const whisperPath = path.join(process.cwd(), "whisper.cpp");

const out = await transcribe({
  inputPath: path.join(dir, "audio16k.wav"),
  whisperPath,
  whisperCppVersion: "1.7.6",
  model,
  language: "es",
  tokenLevelTimestamps: true,
  splitOnWord: true,
  printOutput: false,
  onProgress: (p) => process.stdout.write(`\r${Math.round(p * 100)}%`),
});
const { captions } = toCaptions({ whisperCppOutput: out });
fs.writeFileSync(path.join(dir, "captions.json"), JSON.stringify(captions, null, 1));
fs.writeFileSync(
  path.join(dir, "transcripcion.txt"),
  out.transcription.map((t) => `[${t.timestamps.from} → ${t.timestamps.to}] ${t.text.trim()}`).join("\n"),
);
console.log(`\n${captions.length} palabras → ${dir}`);
