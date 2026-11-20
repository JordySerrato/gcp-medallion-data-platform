
from pathlib import Path
import duckdb

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "warehouse" / "medallion.duckdb"

# ==========================================
# 2. CONECTAR A DUCKDB
# ==========================================

con = duckdb.connect(str(DB_PATH))

try:
    # ======================================
    # 3. TRANSFORMACIÓN BRONZE -> SILVER
    # ======================================

    con.execute("""
        CREATE OR REPLACE TABLE silver_ventas AS

        WITH datos_limpios AS (
            SELECT
                NULLIF(TRIM(venta_id), '') AS venta_id,

                TRY_CAST(fecha AS DATE) AS fecha,

                NULLIF(TRIM(producto_id), '') AS producto_id,

                NULLIF(TRIM(producto), '') AS producto,

                NULLIF(TRIM(categoria), '') AS categoria,

                TRY_CAST(cantidad AS INTEGER) AS cantidad,

                TRY_CAST(
                    precio_unitario AS DECIMAL(18,2)
                ) AS precio_unitario,

                NULLIF(TRIM(tienda), '') AS tienda,

                fecha_ingesta,
                archivo_origen

            FROM bronze_ventas
        ),

        datos_validos AS (
            SELECT *
            FROM datos_limpios
            WHERE venta_id IS NOT NULL
              AND fecha IS NOT NULL
              AND producto_id IS NOT NULL
              AND producto IS NOT NULL
              AND cantidad > 0
              AND precio_unitario >= 0
        ),

        datos_sin_duplicados AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY venta_id
                    ORDER BY fecha_ingesta DESC, archivo_origen DESC
                ) AS numero_fila
            FROM datos_validos
        )

        SELECT
            venta_id,
            fecha,
            producto_id,
            producto,
            categoria,
            cantidad,
            precio_unitario,
            tienda,

            CAST(
                cantidad * precio_unitario
                AS DECIMAL(18,2)
            ) AS importe_total,

            fecha_ingesta,
            archivo_origen

        FROM datos_sin_duplicados
        WHERE numero_fila = 1
    """)

    # ======================================
    # 4. VALIDACIÓN DE RESULTADOS
    # ======================================

    total_bronze = con.execute("""
        SELECT COUNT(*) FROM bronze_ventas
    """).fetchone()[0]

    total_silver = con.execute("""
        SELECT COUNT(*) FROM silver_ventas
    """).fetchone()[0]

    print("Transformación Bronze -> Silver completada")
    print(f"Registros en Bronze: {total_bronze}")
    print(f"Registros en Silver: {total_silver}")
    print(f"Registros excluidos: {total_bronze - total_silver}")

finally:
    con.close()
