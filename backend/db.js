// PostgreSQL bağlantı havuzu (connection pool)
// Ortam değişkenleri .env dosyasından okunur (bkz. .env.example)

const { Pool } = require("pg");

// DATABASE_URL verilmişse onu kullan, yoksa ayrı ayrı değişkenlerden kur.
const pool = process.env.DATABASE_URL
  ? new Pool({ connectionString: process.env.DATABASE_URL })
  : new Pool({
      host: process.env.PGHOST || "localhost",
      port: parseInt(process.env.PGPORT || "5432", 10),
      user: process.env.PGUSER || "postgres",
      password: process.env.PGPASSWORD || "postgres",
      database: process.env.PGDATABASE || "roadscan",
    });

pool.on("error", (err) => {
  console.error("[db] Beklenmeyen havuz hatası:", err.message);
});

module.exports = {
  query: (text, params) => pool.query(text, params),
  pool,
};
