# 🛣️ RoadScan — Akıllı Yol Bozukluğu Tespit Sistemi (Sunum)

> Araç içi dashcam ile yoldaki çukur ve çatlakları yapay zekâ + görüntü işleme ile gerçek zamanlı tespit eden, GPS/zamanla eşleştirip merkezi panele raporlayan tam yığın sistem.

---

## 1. Proje nedir? (Problem → Çözüm)
**Problem:** Belediye/karayolları ekipleri yoldaki çukur ve çatlakları manuel tespit ediyor — yavaş, pahalı, kayıt dağınık.

**Çözüm:** Araca takılı bir kameranın (dashcam) gördüğü yolu **gerçek zamanlı tarayan**, bozuklukları tespit edip **konum + zaman + fotoğrafla** merkezi bir veritabanına raporlayan, harita üzerinde gösteren tam yığın (full-stack) web sistemi. Kurulum gerektirmeden tarayıcıda çalışır.

## 2. Sistem nasıl çalışır? (Uçtan uca)
```
Kamera/Video → Tespit Motoru (tarayıcı: YOLO + görüntü işleme)
        → bozukluk + konum + zaman + kırpılmış foto
        → Backend API (Node/Express) → PostgreSQL veritabanı
        → Yönetim Paneli (Leaflet harita + liste + istatistik)
```
Üç ana modül: **(1) Tespit motoru**, **(2) Backend + veritabanı**, **(3) Yönetim paneli.**

## 3. Projenin gelişimi (iki yaklaşımı da denedik)
- **v1 — Klasik görüntü işleme:** Canny kenar tespiti + morfolojik genişletme + kontur + alan filtresi. Sorun: "çukur" kavramı yok, **her kenarı** (şerit, gölge, doku) bozukluk sanıyordu → aşırı yanlış pozitif.
- **v2 — Yapay zekâ (YOLO):** Çukurun ne olduğunu **öğrenen** bir model eğittik. Yanlış pozitifler ciddi azaldı.
- **v3 — Hibrit (ikisi birlikte):** YOLO tespit eder, **klasik görüntü işleme doğrular.** En sağlam yapı bu.

---

## 4. 🧠 MODEL (Yapay Zekâ) kısmı
- **Model:** YOLOv8s (Ultralytics) — gerçek zamanlı nesne tespiti, hafif sürüm (edge cihaz dostu).
- **Transfer learning:** COCO ön-eğitimli ağırlıklardan başlatıp yol-hasarı verisiyle ince ayar.
- **Veri (en güçlü yanımız):** 3 açık veri seti **birleştirildi** → **~46.000 görüntü, 4 sınıf:**
  - Boyuna Çatlak · Enine Çatlak · Timsah Sırtı Çatlak · **Çukur**
  - Kaynaklar: **RDD2022** (6 ülke, çatlaklar) + **BharatPotHole** (~7k çukur) + **IVCNZ** (çukur). Çukur sınıfını 3 kaynaktan birden besledik.
- **Eğitim:** Kendi GPU'muzda (RTX 5060), 80 epoch, ~13 saat.
- **Sonuç (doğrulama, mAP@50):** Genel **0.61** · Timsah 0.68 · Boyuna/Enine 0.60 · Çukur 0.56.
- **Dağıtım:** Model **ONNX** formatına aktarıldı → **tarayıcıda, internetsiz** çalışıyor (ONNX Runtime Web, WebGPU/WASM). Aynı ONNX ileride telefon / Raspberry Pi / Jetson'da da koşar.

## 5. 🖼️ GÖRÜNTÜ İŞLEME kısmı
**a) Ön işleme (model girişi):**
- **Letterbox** ile kareyi en-boy oranını koruyarak 640×640'a getirme
- Gri/normalize → **Float32 NCHW tensör**

**b) Son işleme (model çıkışı):**
- Ham çıktıyı (`[1, 8, 8400]`) ayrıştırma
- Güven eşiği + **NMS (Non-Max Suppression)** ile çakışan kutuları eleme (geometrik IoU)
- Kutuları letterbox'tan orijinal koordinata geri ölçekleme

**c) Hibrit doğrulama (klasik CV — can alıcı kısım):**
Bir tespit "Kritik" sayılıp panele gitmeden önce klasik görüntü işleme ile sınanır:
- **ROI analizi:** Kutu görüntünün üst kısmındaysa (gökyüzü/bina/ağaç) → ele. Çukur yolda = alt bölgede.
- **Doku/kenar analizi:** Bölge **gri tonlamaya** çevrilir, **gradyan (Sobel benzeri kenar yoğunluğu)** hesaplanır. Düz/tek renk yüzeyler (araç paneli, duvar, boş asfalt) → ele; gerçek bozuklukta kenar/doku vardır.

**d) Diğer görüntü işleme adımları:**
- **Severity (önem):** Kutu alanının kareye oranına göre Küçük/Orta/Kritik
- **Kırpma:** Tespit edilen bölge kesilip panele yakın-çekim gönderilir
- **Kare-arası takip (IoU):** Aynı çukur videoda yüzlerce karede görünse de **tek kayıt**

## 6. 📋 Akıllı raporlama (veritabanı şişmesin)
- **Ekranda 3 kademe de** kutulanır (operatör her şeyi görür)
- **Panele yalnızca Kritik** + CV doğrulamasından geçenler gider → DB temiz, sadece ciddi/yolculuğu etkileyen bozukluklar
- Aynı bozukluk takip + kalıcılık şartıyla tek kez kaydedilir

## 7. 💻 Backend + Panel
- **Backend:** Node.js/Express REST API, **PostgreSQL**, görüntüler `/uploads`'a dosya olarak, CORS açık. Endpoint'ler: kayıt ekle/listele/filtrele/istatistik/sil.
- **Panel:** Leaflet haritada renk kodlu pinler, kırpılmış görüntü listesi, tür/severity/tarih filtreleri, özet istatistik kartları, 30 sn'de bir otomatik yenileme.

## 8. 🚌 Vizyon (pazarlanabilirlik)
Her otobüse küçük bir cihaz + kamera → model **yerinde, offline** çalışır, çukurları GPS'le işaretler, bağlantı gelince merkeze yollar. Model küçük (ONNX) olduğu için ucuz donanımda (Raspberry Pi / RK3588 / Jetson) koşabilir.

## 9. 🛠️ Teknoloji yığını
Vanilla JS · Canvas/OpenCV görüntü işleme · **YOLOv8 (PyTorch / Ultralytics)** · **ONNX Runtime Web** · Node.js / Express · PostgreSQL · Leaflet.js

## 10. ⚖️ Dürüst sınırlar + gelecek
- Model açık kaynak (Hindistan/Japonya ağırlıklı) veriyle eğitildi → **Türk yollarında recall sınırlı.** Eşik + CV filtresi yardımcı olur ama tavanı veri belirler.
- **Sıradaki adımlar:** Türk yolu görüntüleriyle **fine-tune** (model boyutu değişmeden doğruluk artar) · GPS entegrasyonu + konum kümeleme · store-and-forward (offline kuyruk) · native edge dağıtımı (INT8).

---

## 🎤 Olası sorular → cevaplar
- **"Neden klasik görüntü işleme değil, derin öğrenme?"** → Klasik yöntem (v1, Canny) "çukur" kavramını bilmiyor, her kenarı yakalıyordu; YOLO öğreniyor. Klasik CV'yi **doğrulama katmanı** olarak geri kattık (hibrit).
- **"mAP nedir, 0.61 iyi mi?"** → Ortalama hassasiyet (precision–recall alanı). Gerçek, çok-ülkeli, 4-sınıflı yol hasarı verisinde literatür ~0.6–0.75; bizimki makul. Çukurda fine-tune ile artar.
- **"Modeli nasıl eğittiniz?"** → 3 veri setini birleştirip (46k) transfer learning ile YOLOv8s'i kendi GPU'muzda eğittik.
- **"Gerçek zamanlı mı?"** → Evet, tarayıcıda WebGPU/WASM ile; araçta saniyede birkaç kare yeterli (otobüs hızında).
- **"Neden tarayıcıda / offline?"** → Araçta internet olmayabilir; ONNX ile cihaz üstü çalışır, sunucu gerekmez.
- **"Yanlış pozitifleri nasıl azalttınız?"** → Üç katman: yüksek raporlama eşiği + sadece Kritik + klasik CV doğrulaması (ROI + doku).
