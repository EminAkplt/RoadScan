# RoadScan — Yapay Zekâ Tespit Modeli Entegrasyon Planı

> Hedef: Klasik kenar tespitini, **kendi eğittiğimiz YOLOv8 modeliyle** değiştirmek.
> Model tarayıcıda/cihazda **yerel ve internetsiz** çalışacak (ONNX Runtime Web).
> GPU (RTX 5060) yalnızca **modeli eğitmek** için kullanılır; son kullanıcıya GPU gerekmez.

## Mimari karar
- **Tespit nerede:** Tarayıcıda, cihaz üzerinde (offline). Model `.onnx` + ONNX Runtime Web `.wasm` dosyaları projeye gömülü → internetsiz çalışır.
- **Model:** Kendi eğittiğimiz **YOLOv8n** (tarayıcıda hızlı, ~6–12 MB).
- **Backend:** Değişmiyor (Node/Express/PostgreSQL kayıt + panel akışı aynı kalır).

---

## Aşama 0 — Eğitim ortamı (Python + GPU)
- `training/` altında Python 3.12 sanal ortamı (mevcut pip/Python sürüm karışıklığını izole eder).
- RTX 5060 (Blackwell) için **PyTorch CUDA (cu128, torch ≥ 2.7)** + `ultralytics` kurulumu.
- `torch.cuda.is_available()` ve GPU doğrulaması.
- ⚠️ Büyük indirme (~2.5 GB torch). Tek seferlik.

## Aşama 1 — Veri seti
- Ücretsiz pothole veri seti (YOLO formatı) indir.
  - 1. tercih: doğrudan indirilebilen (GitHub/Kaggle) bir set.
  - Gerekirse senden **ücretsiz Roboflow API anahtarı** isteyeceğim (tek satır).
- `training/dataset/` altına aç, `data.yaml` hazırla.
- Veri seti `.gitignore`'a eklenir (repoya gitmez, büyük).

## Aşama 2 — Eğitim
- YOLOv8n, `imgsz=640`, GPU'ya göre batch, ~50–100 epoch.
- RTX 5060'ta tahmini ~1–2 saat (veri boyutuna göre).
- Çıktı: `runs/.../best.pt` + mAP metrikleri.

## Aşama 3 — ONNX'e dışa aktar
- `best.pt → pothole.onnx` (opset, imgsz 640, simplify).
- `frontend/models/pothole.onnx` içine koy (repoya dahil — ürünün parçası).

## Aşama 4 — Frontend (tarayıcıda çıkarım)
- OpenCV.js Canny pipeline'ı **kaldır**, yerine **ONNX Runtime Web**.
- `onnxruntime-web` ve `.wasm` dosyalarını **yerel** servis et (CDN yok → offline).
- Ön işleme: letterbox 640×640, normalize, NCHW Float32.
- Son işleme: eşik + **NMS** (JS'te), kutuları orijinal boyuta ölçekle.
- Çizim + severity (kutu alanı + güven skoru → Küçük/Orta/Kritik korunur).
- 3 kaynak (foto/video/webcam), snapshot, backend'e POST **aynen korunur**.

## Aşama 5 — Entegrasyon + test
- Express, `models/` ve `.wasm` dosyalarını doğru servis etsin.
- Örnek çukur fotoğrafı/videosuyla uçtan uca test.
- README + PLAN güncelle (eğitim adımları, offline notu).

## Aşama 6 — Commit & push
- Temiz commit (Claude attribution yok), RoadScan reposuna push.
- `.onnx` + `.wasm` repoda; **veri seti ve venv repoda değil**.

---

## Edge / pazarlanabilirlik (mini cihazlar)
- Çıktı **ONNX** = evrensel, taşınabilir format. Aynı model:
  - Tarayıcıda (referans demo, her cihaz/telefon) — bu repo
  - Native edge runtime'da (Raspberry Pi / Jetson / gömülü kart) — ileride aynı `.onnx`
- **YOLOv8n** zaten edge için tasarlanmış en hafif sürüm.
- Çok zayıf cihazlar için **INT8 quantization** (model ~4× küçülür, hızlanır) opsiyonu Aşama 3'e eklenir.
- "Bugün eğitilen model = yarın cihaza konacak model" — ekstra eğitim gerekmez, sadece runtime değişir.

## Riskler / notlar
- **RTX 50-serisi CUDA:** Doğru torch wheel'i (cu128) şart; kurulumda dikkat.
- **Tarayıcı hızı:** YOLOv8n WASM'de birkaç FPS; WebGPU varsa çok daha hızlı. Canlı videoda yeterli.
- **Doğruluk = veri:** Hazır veri seti Türk yollarına %100 uymayabilir; ileride kendi görüntülerimizle iyileştirilebilir (v2).
- İlk sürüm "çalışır + belirgin doğruluk artışı" hedefler; mükemmel saha doğruluğu kendi verimizle gelir.
