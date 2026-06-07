// RoadScan — Veri Kayıt Servisi + API (Modül 2 ve Modül 4)
// Express tabanlı REST API. Tespit kayıtlarını PostgreSQL'e yazar,
// snapshot görüntülerini /uploads klasörüne dosya olarak saklar.

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const db = require("./db");

const app = express();
const PORT = parseInt(process.env.PORT || "3000", 10);

const UPLOADS_DIR = path.join(__dirname, "uploads");
const FRONTEND_DIR = path.join(__dirname, "..", "frontend");

// uploads klasörü yoksa oluştur
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

// ---- Middleware ----
app.use(cors()); // CORS açık: frontend farklı port'tan istek atabilir
app.use(express.json({ limit: "15mb" })); // base64 görüntüler büyük olabilir
app.use("/uploads", express.static(UPLOADS_DIR));
app.use(express.static(FRONTEND_DIR)); // index.html ve panel.html servis et

// data:image/jpeg;base64,... → dosyaya yaz, göreli yol döndür
function saveBase64Image(dataUrl) {
  if (!dataUrl || typeof dataUrl !== "string") return null;
  const match = dataUrl.match(/^data:image\/(jpeg|jpg|png);base64,(.+)$/);
  if (!match) return null;

  const ext = match[1] === "png" ? "png" : "jpg";
  const buffer = Buffer.from(match[2], "base64");
  const fileName = `det_${Date.now()}_${Math.round(
    Number(process.hrtime.bigint() % 1000000n)
  )}.${ext}`;
  fs.writeFileSync(path.join(UPLOADS_DIR, fileName), buffer);
  return `/uploads/${fileName}`;
}

// =====================================================================
//  MODÜL 2 — POST /api/detections  (yeni tespit kaydı)
// =====================================================================
app.post("/api/detections", async (req, res) => {
  try {
    const { lat, lng, timestamp, severity, confidence, image } = req.body;

    if (
      typeof lat !== "number" ||
      typeof lng !== "number" ||
      !timestamp ||
      !severity ||
      typeof confidence !== "number"
    ) {
      return res
        .status(400)
        .json({ success: false, error: "Eksik veya hatalı alanlar" });
    }

    const imagePath = saveBase64Image(image);

    const result = await db.query(
      `INSERT INTO detections (lat, lng, timestamp, severity, confidence, image_path)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id`,
      [lat, lng, timestamp, severity, confidence, imagePath]
    );

    res.json({ success: true, id: result.rows[0].id });
  } catch (err) {
    console.error("[POST /api/detections]", err.message);
    res.status(500).json({ success: false, error: "Sunucu hatası" });
  }
});

// =====================================================================
//  MODÜL 4 — GET /api/detections  (tümü veya ?severity= ile filtreli)
// =====================================================================
app.get("/api/detections", async (req, res) => {
  try {
    const { severity } = req.query;
    let result;
    if (severity) {
      result = await db.query(
        "SELECT * FROM detections WHERE severity = $1 ORDER BY timestamp DESC",
        [severity]
      );
    } else {
      result = await db.query(
        "SELECT * FROM detections ORDER BY timestamp DESC"
      );
    }
    res.json(result.rows);
  } catch (err) {
    console.error("[GET /api/detections]", err.message);
    res.status(500).json({ error: "Sunucu hatası" });
  }
});

// =====================================================================
//  MODÜL 4 — GET /api/detections/stats  (özet istatistikler)
// =====================================================================
app.get("/api/detections/stats", async (req, res) => {
  try {
    const total = await db.query("SELECT COUNT(*)::int AS c FROM detections");
    const critical = await db.query(
      "SELECT COUNT(*)::int AS c FROM detections WHERE severity = 'Kritik'"
    );
    const last24 = await db.query(
      "SELECT COUNT(*)::int AS c FROM detections WHERE created_at >= NOW() - INTERVAL '24 hours'"
    );

    // En yoğun bölge: koordinatları ~111 m'lik kareye yuvarlayıp kümele
    const hotspot = await db.query(
      `SELECT ROUND(lat::numeric, 3) AS glat,
              ROUND(lng::numeric, 3) AS glng,
              COUNT(*)::int AS c
       FROM detections
       GROUP BY glat, glng
       ORDER BY c DESC
       LIMIT 1`
    );

    res.json({
      total: total.rows[0].c,
      critical: critical.rows[0].c,
      last24h: last24.rows[0].c,
      hotspot: hotspot.rows[0]
        ? {
            lat: Number(hotspot.rows[0].glat),
            lng: Number(hotspot.rows[0].glng),
            count: hotspot.rows[0].c,
          }
        : null,
    });
  } catch (err) {
    console.error("[GET /api/detections/stats]", err.message);
    res.status(500).json({ error: "Sunucu hatası" });
  }
});

// =====================================================================
//  MODÜL 4 — DELETE /api/detections/:id  (kaydı sil)
// =====================================================================
app.delete("/api/detections/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (Number.isNaN(id)) {
      return res.status(400).json({ success: false, error: "Geçersiz id" });
    }

    const found = await db.query(
      "SELECT image_path FROM detections WHERE id = $1",
      [id]
    );
    if (found.rowCount === 0) {
      return res.status(404).json({ success: false, error: "Kayıt bulunamadı" });
    }

    // İlişkili görüntü dosyasını da sil
    const imagePath = found.rows[0].image_path;
    if (imagePath) {
      const abs = path.join(__dirname, imagePath.replace(/^\//, ""));
      fs.promises.unlink(abs).catch(() => {}); // dosya yoksa sessiz geç
    }

    await db.query("DELETE FROM detections WHERE id = $1", [id]);
    res.json({ success: true });
  } catch (err) {
    console.error("[DELETE /api/detections/:id]", err.message);
    res.status(500).json({ success: false, error: "Sunucu hatası" });
  }
});

// Basit sağlık kontrolü
app.get("/api/health", (req, res) => res.json({ ok: true }));

app.listen(PORT, () => {
  console.log(`\n🛣️  RoadScan API çalışıyor → http://localhost:${PORT}`);
  console.log(`   Tespit motoru : http://localhost:${PORT}/index.html`);
  console.log(`   Yönetim paneli: http://localhost:${PORT}/panel.html\n`);
});
