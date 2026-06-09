# RoadScan — Geliştirme Planı ve Mevcut Durum

> Araç içi dashcam ile yol bozukluğu (çukur + çatlak) tespiti. Model **tarayıcıda, cihaz üstü, offline** çalışır (ONNX Runtime Web). Hedef: küçük donanımlarda (otobüs/araç) çalışabilen, pazarlanabilir bir edge sistemi.

## ✅ Tamamlananlar

### Mimari
- **Tespit motoru** (`frontend/index.html`): YOLOv8 ONNX, ONNX Runtime Web (WebGPU + WASM yedeği), tamamen offline.
- **Backend** (`backend/`): Node/Express + PostgreSQL; `detections` tablosu (lat/lng/timestamp/severity/label/confidence/image_path).
- **Yönetim paneli** (`frontend/panel.html`): Leaflet harita, kırpılmış görüntü listesi, tür/severity/tarih filtreleri, tür dağılımı, istatistik kartları.

### Model (çok sınıflı, 4 sınıf: Boyuna/Enine/Timsah Çatlak + Çukur)
- Üç açık veri seti **birleştirildi** (`training/merge_datasets.py`):
  RDD2022 + BharatPotHole + IVCNZ → **~46.000 görüntü**, çukur 3 kaynaktan beslendi.
- **YOLOv8s** sıfırdan eğitildi (RTX 5060, 80 epoch, ~13 saat) — `training/train.py`.
- Doğrulama: **mAP@50 ≈ 0.61** (timsah 0.68 / enine 0.60 / boyuna 0.60 / çukur 0.56).
- **640px eğit → 960px çıkarım** export edildi (`training/export.py`) → `frontend/models/road_damage.onnx`.

### Raporlama mantığı (DB'yi şişirmeden)
- **Ekranda 3 kademe de** (Küçük/Orta/Kritik) kutulanır.
- **Panele yalnızca Kritik** gönderilir (ciddi/yolculuğu etkileyen).
- **Kare-arası IoU takibi** → aynı fiziksel bozukluk videoda tek kayıt.
- Kalıcılık (N ardışık kare) + ayrı raporlama güven eşiği.
- Tespit edilen bölge **kırpılıp** panele yakın-çekim olarak gider.
- Tüm eşikler kod içinde sabit — **son kullanıcı hassasiyet ayarı yok.**

### Edge / pazarlanabilirlik
- Çıktı **ONNX** (taşınabilir): tarayıcı + ileride native (Raspberry Pi / Jetson / telefon).
- Frame sampling (~4 FPS) — küçük donanım için hesap yükü düşük.
- INT8 quantization opsiyonu (`export.py --int8`).

## 🔧 Mevcut sınır (bilinen)
- Model **Hindistan/Japonya** ağırlıklı veriyle eğitildi → **Türk yollarında** (özellikle suyla dolu/aşırı kırık çukurlarda) **recall sınırlı.** Eşik düşürmek bir miktar yardımcı olur ama tavanı modelin verisi belirler.

## 🗺️ Sıradaki adımlar
1. **Türk verisiyle fine-tune (en yüksek etki):** sahadan/otobüs videolarından 100-500 kare etiketle → mevcut modeli ince ayarla. Domain uyunca çukur recall'ı belirgin artar (model boyutu/hızı değişmeden).
2. **GPS entegrasyonu:** gerçek koordinat + sunucuda ~15-20 m GPS kümeleme (aynı çukur tek kayıt).
3. **Store-and-forward:** araçta internet kesik olduğunda lokal kuyruk + bağlantı gelince senkron.
4. **Native edge dağıtımı:** aynı ONNX'i otobüs içi küçük cihaza (Pi/RK3588/Jetson) taşı, INT8 ile hızlandır.

## 📁 İlgili dosyalar
- `training/merge_datasets.py` — 3 veri setini birleştirir (4 sınıf)
- `training/train.py` — YOLOv8 eğitimi
- `training/export.py` — best.pt → ONNX (960px / opsiyonel INT8)
- `frontend/models/road_damage.onnx` — dağıtılan model
