
from pathlib import Path
import duckdb

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "warehouse" / "medallion.duckdb"

# ==========================================
# 2. CONEXIÓN A DUCKDB
# ==========================================

con = duckdb.connect(str(DB_PATH))

try:
    con.execute("BEGIN TRANSACTION")

    # ======================================
    # 3. INDICADORES GENERALES
    # ======================================

    con.execute("""
        CREATE OR REPLACE TABLE gold_ventas_resumen AS
        SELECT
            COUNT(*) AS total_transacciones,
            COALESCE(SUM(cantidad), 0) AS unidades_vendidas,
            COALESCE(SUM(importe_total), 0) AS ventas_totales,
            COUNT(DISTINCT tienda) AS total_tiendas,
            COUNT(DISTINCT producto_id) AS total_productos,
            COALESCE(
                ROUND(AVG(importe_total), 2), 0
            ) AS ticket_promedio
        FROM silver_ventas
    """)

    # ======================================
    # 4. VENTAS POR TIENDA
    # ======================================

    con.execute("""
        CREATE OR REPLACE TABLE gold_ventas_tienda AS
        SELECT
            tienda,
            COUNT(*) AS total_transacciones,
            SUM(cantidad) AS unidades_vendidas,
            SUM(importe_total) AS ventas_totales
        FROM silver_ventas
        GROUP BY tienda
    """)

    # ======================================
    # 5. VENTAS POR PRODUCTO
    # ======================================

    con.execute("""
        CREATE OR REPLACE TABLE gold_ventas_producto AS
        SELECT
            producto_id,
            producto,
            categoria,
            SUM(cantidad) AS unidades_vendidas,
            SUM(importe_total) AS ventas_totales
        FROM silver_ventas
        GROUP BY producto_id, producto, categoria
    """)

    # ======================================
    # 6. VENTAS POR CATEGORÍA
    # ======================================

    con.execute("""
        CREATE OR REPLACE TABLE gold_ventas_categoria AS
        SELECT
            categoria,
            COUNT(*) AS total_transacciones,
            SUM(cantidad) AS unidades_vendidas,
            SUM(importe_total) AS ventas_totales
        FROM silver_ventas
        GROUP BY categoria
    """)

    con.execute("COMMIT")

    # ======================================
    # 7. MOSTRAR RESULTADOS
    # ======================================

    resumen = con.execute("""
        SELECT * FROM gold_ventas_resumen
    """).fetchone()

    print("Transformación Silver -> Gold completada")
    print(f"Transacciones: {resumen[0]}")
    print(f"Unidades vendidas: {resumen[1]}")
    print(f"Ventas totales: S/ {resumen[2]}")
    print(f"Tiendas: {resumen[3]}")
    print(f"Productos: {resumen[4]}")
    print(f"Ticket promedio: S/ {resumen[5]}")

except Exception:
    con.execute("ROLLBACK")
    raise

finally:
    con.close()
