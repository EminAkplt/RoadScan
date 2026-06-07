# 🛣️ RoadScan — Akıllı Yol Bozukluğu Tespit Sistemi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Express](https://img.shields.io/badge/Express-4.x-000000?logo=express&logoColor=white)](https://expressjs.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-111F68)](https://docs.ultralytics.com)
[![ONNX Runtime Web](https://img.shields.io/badge/ONNX%20Runtime-Web-005CED?logo=onnx&logoColor=white)](https://onnxruntime.ai)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)](https://leafletjs.com)

Araç ön kamerasından (dashcam) alınan görüntü akışında yoldaki **çukurları (pothole) yapay zekâ ile gerçek zamanlı tespit eden**, her tespiti **GPS koordinatı ve zaman damgasıyla** eşleştirip merkezi bir veritabanına raporlayan tam yığın (full-stack) sistem.

Tespit, **kendi eğittiğimiz bir YOLOv8 nesne tespit modeliyle** yapılır ve model **kullanıcının cihazında, tarayıcıda, internetsiz** çalışır (ONNX Runtime Web). Model **ONNX** formatında olduğu için aynı dosya ileride telefon / Raspberry Pi / Jetson gibi **edge cihazlarda native** de çalıştırılabilir.

---

## ✨ Özellikler

- **Gerçek yapay zekâ tespiti:** Eğitilmiş **YOLOv8n** modeli — klasik kenar tespitinin aksine "çukur" kavramını öğrenmiştir, yanlış pozitifler çok daha az.
- **Tamamen offline / cihaz üstü:** Model ve çalışma zamanı (`.onnx` + `.wasm`) projeye gömülü; çıkarım için internet veya sunucu gerekmez.
- **WebGPU hızlandırma** (varsa) + her cihazda **WASM** yedeği.
- **Üç görüntü kaynağı:** Fotoğraf, video dosyası, canlı webcam (mobilde arka kamera).
- **Severity sınıflandırma:** kutu boyutuna göre Küçük / Orta / Kritik (sarı / turuncu / kırmızı); güven skoru doğrudan modelden gelir.
- **Otomatik raporlama:** tespit anında GPS + zaman + güven + JPEG snapshot paketlenip sunucuya gönderilir.
- **Yönetim paneli:** Leaflet haritada renk kodlu pinler, filtrelenebilir liste, özet istatistik kartları, 30 sn'de bir otomatik yenileme.
- **Tamamen Türkçe arayüz**, mobil uyumlu, framework'süz vanilla JS.

---

## 🏗️ Mimari

```
┌──────────────────────────────┐   POST /api/detections    ┌──────────────────────────┐
│  Tespit Motoru (tarayıcı)    │ ────────────────────────► │  Express API (backend)   │
│  frontend/index.html         │  (GPS + zaman + severity  │  backend/server.js       │
│  YOLOv8 .onnx + ONNX RT Web  │   + güven + base64 foto)  │  • snapshot → /uploads   │
│  (cihazda, offline çıkarım)  │                           │  • kayıt → PostgreSQL    │
└──────────────────────────────┘                           │  CORS açık               │
                                                            └────────────┬─────────────┘
┌──────────────────────────────┐  GET /api/detections,/stats           │
│  Yönetim Paneli              │ ◄──────────────────────── DELETE /:id  │
│  frontend/panel.html         │                              ┌─────────▼─────────┐
│  Leaflet.js                  │                              │   PostgreSQL      │
└──────────────────────────────┘                              └───────────────────┘

  Model eğitimi (ayrı, tek seferlik):  training/  →  YOLOv8 (RTX GPU)  →  best.pt  →  pothole.onnx
```

### Tespit akışı (cihaz üstü)

1. Kare → **letterbox** ile 640×640'a getirilir, normalize edilir (Float32 NCHW).
2. **YOLOv8 ONNX** modeli çıkarım yapar (WebGPU veya WASM).
3. Çıktı ayrıştırılır, **NMS** ile çakışan kutular elenir, kutular orijinal boyuta ölçeklenir.
4. Kutu + severity etiketi çizilir; en güçlü tespit GPS/zaman/snapshot ile sunucuya gönderilir.

### Severity & Güven

| Kutu alanı / kare oranı | Severity | Renk |
|--------------------------|----------|------|
| < %2 | Küçük | 🟡 Sarı |
| %2 – %6 | Orta | 🟠 Turuncu |
| ≥ %6 | Kritik | 🔴 Kırmızı |

Güven skoru doğrudan modelin tespit güveninden (0.0–1.0) gelir. Eşik ve IoU değerleri arayüzdeki sliderlardan ayarlanabilir.

---

## 🚀 Kurulum

### Gereksinimler
- [Node.js](https://nodejs.org) ≥ 18
- [PostgreSQL](https://www.postgresql.org) ≥ 14
- (Sadece model eğitmek için) [Python](https://www.python.org) 3.10–3.12 + tercihen NVIDIA GPU

### 1) Uygulama (backend + frontend)

```bash
npm install            # bağımlılıklar + ONNX Runtime Web dosyaları (postinstall) kopyalanır
cp .env.example .env   # PostgreSQL bilgilerini düzenle
npm run db:init        # tabloları kur
npm start
```

- **Tespit motoru:** http://localhost:3000/index.html
- **Yönetim paneli:** http://localhost:3000/panel.html

> ⚠️ Tespit motorunun çalışması için eğitilmiş model gerekir: `frontend/models/pothole.onnx`.
> Modeli aşağıdaki adımlarla kendiniz eğitip oluşturabilirsiniz (repoda hazır model de bulunabilir).

### 2) Modeli eğitme (opsiyonel — `training/`)

```bash
cd training
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
# NVIDIA GPU için PyTorch (Blackwell/RTX 50xx: cu128):
.venv\Scripts\python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

.venv\Scripts\python prep_dataset.py   # veri setini indir/hazırla → data.yaml
.venv\Scripts\python train.py          # RTX GPU'da eğit → runs/.../best.pt
.venv\Scripts\python export.py         # best.pt → frontend/models/pothole.onnx
```

### Örnek `.env`

```env
PORT=3000
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=postgres
PGDATABASE=roadscan
```

---

## 📡 API Referansı

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| `POST` | `/api/detections` | Yeni tespit kaydı (snapshot dosyaya yazılır) |
| `GET` | `/api/detections` | Tüm tespitler |
| `GET` | `/api/detections?severity=Kritik` | Severity'e göre filtreli |
| `GET` | `/api/detections/stats` | Özet istatistikler |
| `DELETE` | `/api/detections/:id` | Kaydı ve görüntüyü sil |
| `GET` | `/api/health` | Sağlık kontrolü |

`POST /api/detections` gövdesi:

```json
{ "lat": 41.0082, "lng": 28.9784, "timestamp": "2024-01-15T14:32:00Z",
  "severity": "Kritik", "confidence": 0.87, "image": "data:image/jpeg;base64,..." }
```

---

## 🗄️ Veritabanı Şeması

```sql
CREATE TABLE detections (
  id SERIAL PRIMARY KEY,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  severity VARCHAR(20) NOT NULL,
  confidence FLOAT NOT NULL,
  image_path TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📁 Klasör Yapısı

```
RoadScan/
├── frontend/
│   ├── index.html         # Tespit motoru (YOLO + ONNX Runtime Web)
│   ├── panel.html         # Yönetim paneli (Leaflet)
│   ├── models/            # pothole.onnx + model_meta.json (eğitim çıktısı)
│   └── vendor/ort/        # ONNX Runtime Web dosyaları (npm install ile üretilir)
├── backend/
│   ├── server.js          # Express API
│   ├── db.js              # PostgreSQL bağlantısı
│   ├── init-db.js         # Şema kurulumu
│   ├── schema.sql
│   └── uploads/           # Snapshot görüntüleri
├── training/              # Model eğitimi (Python/Ultralytics) — repoya veri/venv dahil değil
│   ├── prep_dataset.py    # veri seti indir + train/val böl + data.yaml
│   ├── train.py           # YOLOv8 eğitimi
│   ├── export.py          # best.pt → ONNX
│   └── requirements.txt
├── scripts/copy-ort.js    # ONNX RT Web dosyalarını frontend'e kopyalar
├── .env.example
├── package.json
├── LICENSE                # MIT
└── README.md
```

---

## 📱 Edge / pazarlanabilirlik

Eğitilen model **ONNX** formatındadır — taşınabilir ve evrenseldir:
- **Tarayıcı** (bu repo): her cihazda, telefon dahil, offline.
- **Native edge** (ileride): aynı `pothole.onnx` Raspberry Pi / Jetson / mobil üzerinde ONNX Runtime / TensorRT / TFLite ile çalıştırılabilir.
- **YOLOv8n** edge için en hafif sürümdür; çok zayıf cihazlar için **INT8 quantization** (`export.py --int8`) ile model ~4× küçültülebilir.

---

## ⚠️ Notlar

- Modelin doğruluğu eğitildiği veriye bağlıdır. İlk sürüm açık kaynak bir pothole veri setiyle eğitilir; sahaya (Türk yolları, dashcam açısı) özel görüntülerle yeniden eğitilerek doğruluk artırılabilir.
- GPS izni verilmezse varsayılan olarak İstanbul koordinatı kullanılır.
- Threaded WASM için tarayıcı SharedArrayBuffer ister; bu olmadan ONNX Runtime tek iş parçacıklı WASM ya da WebGPU ile çalışır (sorun olmaz).

---

## 📄 Lisans

[MIT](LICENSE) © Mehmet Emin AKPOLAT
