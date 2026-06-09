# 🛣️ RoadScan — Akıllı Yol Bozukluğu Tespit Sistemi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Express](https://img.shields.io/badge/Express-4.x-000000?logo=express&logoColor=white)](https://expressjs.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-111F68)](https://docs.ultralytics.com)
[![ONNX Runtime Web](https://img.shields.io/badge/ONNX%20Runtime-Web-005CED?logo=onnx&logoColor=white)](https://onnxruntime.ai)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)](https://leafletjs.com)

Araç ön kamerasından (dashcam) alınan görüntü akışında yoldaki **bozuklukları (çukur ve çatlak türleri) yapay zekâ ile gerçek zamanlı tespit eden**, her tespiti **GPS koordinatı ve zaman damgasıyla** eşleştirip, tespit edilen bölgeyi **kırparak** merkezi bir veritabanına raporlayan tam yığın (full-stack) sistem.

Tespit, **çok sınıflı bir YOLOv8 yol-hasarı modeliyle** yapılır ve model **kullanıcının cihazında, tarayıcıda, internetsiz** çalışır (ONNX Runtime Web). Model **ONNX** formatında olduğu için aynı dosya ileride telefon / Raspberry Pi / Jetson gibi **edge cihazlarda native** de çalıştırılabilir.

### Tespit edilen bozukluk türleri

| Sınıf (model) | Türkçe | İkon |
|---------------|--------|------|
| Longitudinal Crack | Boyuna Çatlak | ↕️ |
| Transverse Crack | Enine Çatlak | ↔️ |
| Alligator Crack | Timsah Sırtı Çatlak | 🐊 |
| Potholes | Çukur | 🕳️ |

---

## ✨ Özellikler

- **Gerçek yapay zekâ tespiti:** Eğitilmiş **çok sınıflı YOLOv8** modeli — çukura ek olarak **3 çatlak türünü** de ayırt eder; klasik kenar tespitine göre çok daha az yanlış pozitif.
- **Tespit kırpma:** Bulunan her bozukluğun bölgesi kırpılıp panele yakın-çekim olarak gönderilir.
- **Tamamen offline / cihaz üstü:** Model ve çalışma zamanı (`.onnx` + `.wasm`) projeye gömülü; çıkarım için internet veya sunucu gerekmez.
- **WebGPU hızlandırma** (varsa) + her cihazda **WASM** yedeği.
- **Üç görüntü kaynağı:** Fotoğraf, video dosyası, canlı webcam (mobilde arka kamera).
- **Severity sınıflandırma:** kutu boyutuna göre Küçük / Orta / Kritik (sarı / turuncu / kırmızı). **Üç kademe de ekranda kutulanır; panele yalnızca Kritik gönderilir** (DB gereksiz kayıtla şişmez).
- **Otomatik raporlama:** Kritik tespit anında GPS + zaman + tür + güven + kırpılmış JPEG paketlenip sunucuya gönderilir.
- **Yönetim paneli:** Leaflet haritada renk kodlu pinler, tür/severity/tarih filtreleri, kırpılmış görüntü listesi, tür dağılımı ve özet istatistik kartları, 30 sn'de bir otomatik yenileme.
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

1. Kare → **letterbox** ile 960×960'a getirilir, normalize edilir (Float32 NCHW).
2. **YOLOv8 ONNX** modeli çıkarım yapar (WebGPU veya WASM).
3. Çıktı ayrıştırılır, **NMS** ile çakışan kutular elenir, kutular orijinal boyuta ölçeklenir.
4. **Tüm bozukluklar** kutu + severity etiketiyle ekrana çizilir; videoda kare-arası takiple **aynı bozukluk tek kayıt** olur ve **yalnızca Kritik** olanlar GPS/zaman/kırpılmış görüntüyle panele gönderilir.

### Severity & Raporlama

Severity, **tür + kutu boyutuna** göre üç kademedir (eşikler tür bazlı, kod içinde sabit — son kullanıcı ayarı yok):

| Kademe | Renk | Ekranda | Panele |
|--------|------|---------|--------|
| Küçük | 🟡 Sarı | ✅ çizilir | ❌ |
| Orta | 🟠 Turuncu | ✅ çizilir | ❌ |
| **Kritik** | 🔴 Kırmızı | ✅ çizilir | ✅ **gönderilir** |

Böylece operatör ekranda her şeyi görür ama veritabanına yalnızca **ciddi/yolculuğu etkileyen** bozukluklar düşer. Güven skoru doğrudan modelin tespit güveninden (0.0–1.0) gelir.

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

> ⚠️ Tespit motorunun çalışması için model gerekir: `frontend/models/road_damage.onnx` (çok sınıflı yol hasarı modeli).
> Repoda hazır model bulunur; ayrıca aşağıdaki adımlarla kendiniz de eğitebilirsiniz.

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
| `GET` | `/api/detections?severity=Kritik&label=Çukur` | Severity ve/veya türe göre filtreli |
| `GET` | `/api/detections/stats` | Özet istatistikler (+ tür dağılımı `byLabel`) |
| `DELETE` | `/api/detections/:id` | Kaydı ve görüntüyü sil |
| `GET` | `/api/health` | Sağlık kontrolü |

`POST /api/detections` gövdesi:

```json
{ "lat": 41.0082, "lng": 28.9784, "timestamp": "2024-01-15T14:32:00Z",
  "severity": "Kritik", "label": "Çukur", "confidence": 0.87,
  "image": "data:image/jpeg;base64,..." }
```

> `image` artık tespit edilen bölgenin **kırpılmış** görüntüsüdür; `label` bozukluk türüdür.

---

## 🗄️ Veritabanı Şeması

```sql
CREATE TABLE detections (
  id SERIAL PRIMARY KEY,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  severity VARCHAR(20) NOT NULL,
  label VARCHAR(40),            -- bozukluk türü (çukur / çatlak vb.)
  confidence FLOAT NOT NULL,
  image_path TEXT,              -- tespitin kırpılmış görüntüsü
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
│   ├── models/            # road_damage.onnx + model_meta.json (model çıktısı)
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
- **Native edge** (ileride): aynı `road_damage.onnx` Raspberry Pi / Jetson / mobil üzerinde ONNX Runtime / TensorRT / TFLite ile çalıştırılabilir.
- Çok zayıf cihazlar için **INT8 quantization** (`export.py --int8`) ile model ~4× küçültülebilir.

---

## ⚠️ Notlar

- Dağıtılan model, **üç açık kaynak veri setinin birleşimiyle** (RDD2022 + BharatPotHole + IVCNZ Pothole, ~46.000 görüntü, 4 sınıf) sıfırdan eğitilmiş kendi **YOLOv8s** modelimizdir (640px eğitim, 960px çıkarım). Doğrulama mAP@50 ≈ **0.61** (çukur 0.56, timsah çatlak 0.68, boyuna/enine çatlak ~0.60). Eğitim betikleri ve birleştirme aracı `training/` altındadır (`merge_datasets.py`, `train.py`, `export.py`).
- Modelin doğruluğu eğitildiği veriye bağlıdır; sahaya (Türk yolları, dashcam açısı) özel görüntülerle **fine-tune** edilerek artırılabilir — model boyutu/hızı değişmeden.
- GPS izni verilmezse varsayılan olarak İstanbul koordinatı kullanılır.
- Threaded WASM için tarayıcı SharedArrayBuffer ister; bu olmadan ONNX Runtime tek iş parçacıklı WASM ya da WebGPU ile çalışır (sorun olmaz).

---

## 📄 Lisans

[MIT](LICENSE) © Mehmet Emin AKPOLAT
