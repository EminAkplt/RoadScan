-- RoadScan veritabanı şeması (PostgreSQL)

CREATE TABLE IF NOT EXISTS detections (
  id          SERIAL PRIMARY KEY,
  lat         DOUBLE PRECISION NOT NULL,
  lng         DOUBLE PRECISION NOT NULL,
  timestamp   TIMESTAMPTZ NOT NULL,
  severity    VARCHAR(20) NOT NULL,
  confidence  FLOAT NOT NULL,
  image_path  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Sık kullanılan filtre/sıralama için indeksler
CREATE INDEX IF NOT EXISTS idx_detections_severity  ON detections (severity);
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections (timestamp DESC);
