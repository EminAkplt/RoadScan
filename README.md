# 🛣️ RoadScan — Akıllı Yol Bozukluğu Tespit Sistemi

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D18-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![Express](https://img.shields.io/badge/Express-4.x-000000?logo=express&logoColor=white)](https://expressjs.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![OpenCV.js](https://img.shields.io/badge/OpenCV.js-4.10-5C3EE8?logo=opencv&logoColor=white)](https://docs.opencv.org)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)](https://leafletjs.com)

Araç ön kamerasından (dashcam) alınan görüntü akışında yoldaki **çatlak ve çukurları gerçek zamanlı tespit eden**, her tespiti **GPS koordinatı ve zaman damgasıyla** eşleştirip merkezi bir veritabanına raporlayan tam yığın (full-stack) web uygulaması.

Hedef kullanıcı **yol bakım ekipleridir**. Tespit motoru kurulum gerektirmeden tarayıcıda çalışır; tüm görüntü işleme istemci tarafında (OpenCV.js) yapılır.

---

## ✨ Özellikler

- **Üç görüntü kaynağı:** Fotoğraf yükleme, video dosyası, canlı webcam (mobil cihazda arka kamera).
- **Klasik bilgisayarlı görü pipeline'ı** — sunucuya video göndermeden, tamamen tarayıcıda:
  ROI → grayscale → Gaussian blur → Canny → dilation → kontur + alan filtresi.
- **Severity sınıflandırma:** kontur alanına göre Küçük / Orta / Kritik (sarı / turuncu / kırmızı).
- **Otomatik raporlama:** tespit anında GPS + zaman + güven skoru + JPEG snapshot paketlenip sunucuya gönderilir.
- **Yönetim paneli:** Leaflet haritada renk kodlu pinler, filtrelenebilir liste, özet istatistik kartları, 30 sn'de bir otomatik yenileme.
- **Tamamen Türkçe arayüz**, mobil uyumlu, framework'süz vanilla JS.

---

## 🏗️ Mimari

```
┌─────────────────────────┐     POST /api/detections      ┌──────────────────────────┐
│  Tespit Motoru          │  ───────────────────────────► │  Express API (backend)   │
│  frontend/index.html    │  (GPS + zaman + severity      │  backend/server.js       │
│  OpenCV.js, getUserMedia│   + güven + base64 görüntü)   │                          │
└─────────────────────────┘                               │  • snapshot → /uploads   │
                                                           │  • kayıt → PostgreSQL    │
┌─────────────────────────┐   GET /api/detections, /stats │                          │
│  Yönetim Paneli         │  ◄─────────────────────────── │  CORS açık               │
│  frontend/panel.html    │   DELETE /api/detections/:id  └────────────┬─────────────┘
│  Leaflet.js             │                                            │
└─────────────────────────┘                                  ┌─────────▼─────────┐
                                                             │   PostgreSQL      │
                                                             │   detections      │
                                                             └───────────────────┘
```

### Görüntü İşleme Pipeline (istemci tarafı)

| Adım | İşlem | Parametre | Amaç |
|------|-------|-----------|------|
| 1 | ROI kırpma | alt %50 | Sadece yol bölgesini işle |
| 2 | Grayscale | `COLOR_RGBA2GRAY` | Renk bilgisini at |
| 3 | Gaussian Blur | 5×5 kernel | Gürültü azalt |
| 4 | Canny Edge | t1=50, t2=150 | Kenarları çıkar |
| 5 | Dilation | 3×3, 2 iterasyon | Kopuk çizgileri birleştir |
| 6 | Kontur + filtre | alan ≥ 500 px² | Gürültü konturlarını ele |
| 7 | Bounding box | severity rengi | Tespiti işaretle |

### Severity & Güven Skoru

| Kontur alanı | Severity | Renk |
|--------------|----------|------|
| 500 – 2000 px² | Küçük | 🟡 Sarı |
| 2000 – 5000 px² | Orta | 🟠 Turuncu |
| ≥ 5000 px² | Kritik | 🔴 Kırmızı |

Güven skoru, kontur alanı `500–8000 px²` aralığında `0.0–1.0`'a normalize edilerek hesaplanır.

---

## 🚀 Kurulum

### Gereksinimler
- [Node.js](https://nodejs.org) ≥ 18
- [PostgreSQL](https://www.postgresql.org) ≥ 14

### Adımlar

```bash
# 1) Bağımlılıkları yükle
npm install

# 2) Ortam değişkenlerini ayarla
cp .env.example .env
#   .env içindeki PostgreSQL bilgilerini kendine göre düzenle

# 3) Veritabanını oluştur (PostgreSQL çalışıyor olmalı)
createdb roadscan          # yoksa: psql -U postgres -c "CREATE DATABASE roadscan;"

# 4) Tabloları kur
npm run db:init

# 5) Sunucuyu başlat
npm start
```

Ardından tarayıcıda:

- **Tespit motoru:** http://localhost:3000/index.html
- **Yönetim paneli:** http://localhost:3000/panel.html

> 💡 Frontend ve backend aynı port'tan servis edilir; ayrı bir statik sunucuya gerek yoktur.
> Kamera ve GPS özellikleri için tarayıcı izin isteyecektir. (Bazı tarayıcılar `getUserMedia`
> için `localhost` veya HTTPS gerektirir — `localhost` üzerinden çalıştırmak yeterlidir.)

### Örnek `.env`

```env
PORT=3000
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=postgres
PGDATABASE=roadscan
# Alternatif: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/roadscan
```

---

## 📡 API Referansı

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| `POST` | `/api/detections` | Yeni tespit kaydı (snapshot dosyaya yazılır) |
| `GET` | `/api/detections` | Tüm tespitler (tarih sırasına göre) |
| `GET` | `/api/detections?severity=Kritik` | Severity'e göre filtreli liste |
| `GET` | `/api/detections/stats` | Özet istatistikler |
| `DELETE` | `/api/detections/:id` | Kaydı ve ilişkili görüntüyü sil |
| `GET` | `/api/health` | Sağlık kontrolü |

### `POST /api/detections` — istek gövdesi

```json
{
  "lat": 41.0082,
  "lng": 28.9784,
  "timestamp": "2024-01-15T14:32:00Z",
  "severity": "Kritik",
  "confidence": 0.87,
  "image": "data:image/jpeg;base64,..."
}
```

**Yanıt:** `{ "success": true, "id": 12 }`

### `GET /api/detections/stats` — yanıt

```json
{
  "total": 128,
  "critical": 34,
  "last24h": 12,
  "hotspot": { "lat": 41.008, "lng": 28.978, "count": 9 }
}
```

---

## 🗄️ Veritabanı Şeması

```sql
CREATE TABLE detections (
  id          SERIAL PRIMARY KEY,
  lat         DOUBLE PRECISION NOT NULL,
  lng         DOUBLE PRECISION NOT NULL,
  timestamp   TIMESTAMPTZ NOT NULL,
  severity    VARCHAR(20) NOT NULL,
  confidence  FLOAT NOT NULL,
  image_path  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📁 Klasör Yapısı

```
RoadScan/
├── frontend/
│   ├── index.html        # Modül 1 — Tespit motoru (OpenCV.js)
│   └── panel.html        # Modül 3 — Yönetim paneli (Leaflet)
├── backend/
│   ├── server.js         # Modül 2 + 4 — Express API
│   ├── db.js             # PostgreSQL bağlantı havuzu
│   ├── init-db.js        # Şema kurulum betiği (npm run db:init)
│   ├── schema.sql        # Tablo tanımları
│   └── uploads/          # Snapshot görüntüleri (git'e eklenmez)
├── .env.example
├── package.json
├── LICENSE               # MIT
└── README.md
```

---

## ⚠️ Notlar & Sınırlamalar

- Tespit, klasik kenar/kontur tabanlı bir yöntemdir (derin öğrenme modeli değildir).
  Gölge, şerit çizgisi veya yüzey deseni gibi etkenler yanlış pozitif üretebilir;
  parametreler (`Canny` eşikleri, alan filtresi) saha koşullarına göre ayarlanmalıdır.
- GPS izni verilmezse varsayılan olarak İstanbul koordinatları kullanılır.
- Aynı konumdan tekrarlı gönderimi azaltmak için istemcide 8 sn'lik basit bir kümeleme uygulanır.

---

## 📄 Lisans

[MIT](LICENSE) © Mehmet Emin AKPOLAT
