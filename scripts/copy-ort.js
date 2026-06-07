// onnxruntime-web çalışma zamanı dosyalarını frontend/vendor/ort/ altına kopyalar.
// npm install sonrası otomatik çalışır (postinstall). Böylece uygulama
// CDN'siz, tamamen offline çalışır. vendor klasörü git'e eklenmez.

const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "node_modules", "onnxruntime-web", "dist");
const DST = path.join(__dirname, "..", "frontend", "vendor", "ort");

// WebGPU (hızlı) + WASM (her yerde) yedekli çalışma için gerekli dosyalar
const FILES = [
  "ort.webgpu.min.js",
  "ort-wasm-simd-threaded.jsep.wasm",
  "ort-wasm-simd-threaded.jsep.mjs",
];

function main() {
  if (!fs.existsSync(SRC)) {
    console.warn("[copy-ort] onnxruntime-web bulunamadı, atlanıyor (npm install gerekli).");
    return;
  }
  fs.mkdirSync(DST, { recursive: true });
  for (const f of FILES) {
    const src = path.join(SRC, f);
    const dst = path.join(DST, f);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dst);
      console.log(`[copy-ort] ✔ ${f}`);
    } else {
      console.warn(`[copy-ort] ✖ bulunamadı: ${f}`);
    }
  }
  console.log("[copy-ort] ONNX Runtime Web dosyaları hazır → frontend/vendor/ort/");
}

main();
