// Veritabanı tablolarını oluşturur: `npm run db:init`
// schema.sql dosyasını okuyup çalıştırır.

require("dotenv").config();
const fs = require("fs");
const path = require("path");
const db = require("./db");

async function main() {
  const sql = fs.readFileSync(path.join(__dirname, "schema.sql"), "utf-8");
  try {
    await db.query(sql);
    console.log("[init-db] Şema başarıyla uygulandı ✔");
  } catch (err) {
    console.error("[init-db] Hata:", err.message);
    process.exitCode = 1;
  } finally {
    await db.pool.end();
  }
}

main();
