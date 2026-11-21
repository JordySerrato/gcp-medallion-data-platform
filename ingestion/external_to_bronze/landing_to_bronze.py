
import os
import csv
import io
from pathlib import Path

import duckdb
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials

# ==================================================
# 1. CONFIGURACIÓN
# ==================================================


# ==========================================
# CONFIGURACION DEL EMULADOR GCS
# ==========================================

os.environ.setdefault(
    "STORAGE_EMULATOR_HOST",
    "http://127.0.0.1:4444"
)

PROJECT_ID = os.getenv(
    "GCS_PROJECT_ID",
    "local-project"
)

BUCKET_NAME = os.getenv(
    "GCS_BUCKET_NAME",
    "medallion-landing"
)

BLOB_NAME = "ventas/2026/11/20/ventas.csv"


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "warehouse" / "medallion.duckdb"

# ==================================================
# 2. DESCARGAR DESDE LANDING
# ==================================================

client = storage.Client(
    project=PROJECT_ID,
    credentials=AnonymousCredentials()
)

bucket = client.bucket(BUCKET_NAME)
blob = bucket.blob(BLOB_NAME)

csv_bytes = blob.download_as_bytes()
csv_text = csv_bytes.decode("utf-8-sig")

rows = list(csv.DictReader(io.StringIO(csv_text)))

if not rows:
    raise ValueError("El archivo CSV no contiene registros")

print(f"Registros descargados desde Landing: {len(rows)}")

# ==================================================
# 3. CONECTAR A DUCKDB
# ==================================================

con = duckdb.connect(str(DB_PATH))

con.execute("""
    CREATE TABLE IF NOT EXISTS bronze_ventas (
        venta_id VARCHAR,
        fecha VARCHAR,
        producto_id VARCHAR,
        producto VARCHAR,
        categoria VARCHAR,
        cantidad VARCHAR,
        precio_unitario VARCHAR,
        tienda VARCHAR,
        fecha_ingesta TIMESTAMP,
        archivo_origen VARCHAR
    )
""")

# ==================================================
# 4. CARGAR REGISTROS EN BRONZE
# ==================================================

datos = [
    (
        row["venta_id"],
        row["fecha"],
        row["producto_id"],
        row["producto"],
        row["categoria"],
        row["cantidad"],
        row["precio_unitario"],
        row["tienda"],
        BLOB_NAME
    )
    for row in rows
]

try:
    con.execute("BEGIN TRANSACTION")

    # Evitar duplicados al reprocesar el mismo archivo
    con.execute(
        "DELETE FROM bronze_ventas WHERE archivo_origen = ?",
        [BLOB_NAME]
    )

    con.executemany("""
        INSERT INTO bronze_ventas (
            venta_id,
            fecha,
            producto_id,
            producto,
            categoria,
            cantidad,
            precio_unitario,
            tienda,
            fecha_ingesta,
            archivo_origen
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
    """, datos)

    con.execute("COMMIT")

except Exception:
    con.execute("ROLLBACK")
    raise

# ==================================================
# 5. VALIDAR RESULTADO
# ==================================================

total = con.execute("""
    SELECT COUNT(*)
    FROM bronze_ventas
    WHERE archivo_origen = ?
""", [BLOB_NAME]).fetchone()[0]

print("Carga Bronze completada")
print(f"Base de datos: {DB_PATH}")
print(f"Tabla: bronze_ventas")
print(f"Registros almacenados: {total}")

con.close()
