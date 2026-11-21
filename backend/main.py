
from pathlib import Path
import os

from fastapi.encoders import jsonable_encoder
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore
import duckdb
from fastapi import FastAPI, HTTPException

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

app = FastAPI(
    title="GCP Medallion Data Platform API",
    description="API REST para consultar datos analiticos y monitorear el pipeline Medallion",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "warehouse" / "medallion.duckdb"


# ==========================================
# 2. ENDPOINT PRINCIPAL
# ==========================================

@app.get("/")
def inicio():
    return {
        "aplicacion": "GCP Medallion Data Platform",
        "version": "1.0.0",
        "mensaje": "API funcionando correctamente"
    }


# ==========================================
# 3. HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "medallion-backend"
    }


# ==========================================
# 4. CONSULTAR INDICADORES GOLD
# ==========================================

@app.get("/api/ventas/resumen")
def obtener_resumen_ventas():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Base de datos DuckDB no disponible"
        )

    con = None

    try:
        # Conexion en modo solo lectura
        con = duckdb.connect(
            str(DB_PATH),
            read_only=True
        )

        resultado = con.execute("""
            SELECT
                total_transacciones,
                unidades_vendidas,
                ventas_totales,
                total_tiendas,
                total_productos,
                ticket_promedio
            FROM gold_ventas_resumen
        """).fetchone()

        if resultado is None:
            raise HTTPException(
                status_code=404,
                detail="No existen indicadores en Gold"
            )

        return {
            "total_transacciones": resultado[0],
            "unidades_vendidas": resultado[1],
            "ventas_totales": str(resultado[2]),
            "total_tiendas": resultado[3],
            "total_productos": resultado[4],
            "ticket_promedio": str(resultado[5])
        }

    except duckdb.Error as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar la capa Gold"
        ) from error

    finally:
        if con is not None:
            con.close()

# ==========================================
# 5. CONSULTAR VENTAS POR TIENDA
# ==========================================

@app.get("/api/ventas/tiendas")
def obtener_ventas_tiendas():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Base de datos DuckDB no disponible"
        )

    con = None

    try:
        con = duckdb.connect(
            str(DB_PATH),
            read_only=True
        )

        resultados = con.execute("""
            SELECT
                tienda,
                total_transacciones,
                unidades_vendidas,
                ventas_totales
            FROM gold_ventas_tienda
            ORDER BY ventas_totales DESC, tienda
        """).fetchall()

        tiendas = []

        for row in resultados:
            tiendas.append({
                "tienda": row[0],
                "total_transacciones": row[1],
                "unidades_vendidas": row[2],
                "ventas_totales": str(row[3])
            })

        return {
            "total_tiendas": len(tiendas),
            "tiendas": tiendas
        }

    except duckdb.Error as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar ventas por tienda"
        ) from error

    finally:
        if con is not None:
            con.close()

# ==========================================
# 6. CONSULTAR VENTAS POR PRODUCTO
# ==========================================

@app.get("/api/ventas/productos")
def obtener_ventas_productos():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Base de datos DuckDB no disponible"
        )

    con = None

    try:
        con = duckdb.connect(
            str(DB_PATH),
            read_only=True
        )

        resultados = con.execute("""
            SELECT
                producto_id,
                producto,
                categoria,
                unidades_vendidas,
                ventas_totales
            FROM gold_ventas_producto
            ORDER BY ventas_totales DESC, producto_id
        """).fetchall()

        productos = []

        for row in resultados:
            productos.append({
                "producto_id": row[0],
                "producto": row[1],
                "categoria": row[2],
                "unidades_vendidas": row[3],
                "ventas_totales": str(row[4])
            })

        return {
            "total_productos": len(productos),
            "productos": productos
        }

    except duckdb.Error as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar ventas por producto"
        ) from error

    finally:
        if con is not None:
            con.close()

# ==========================================
# 7. CONSULTAR VENTAS POR CATEGORIA
# ==========================================

@app.get("/api/ventas/categorias")
def obtener_ventas_categorias():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Base de datos DuckDB no disponible"
        )

    con = None

    try:
        con = duckdb.connect(
            str(DB_PATH),
            read_only=True
        )

        resultados = con.execute("""
            SELECT
                categoria,
                total_transacciones,
                unidades_vendidas,
                ventas_totales
            FROM gold_ventas_categoria
            ORDER BY ventas_totales DESC, categoria
        """).fetchall()

        categorias = []

        for row in resultados:
            categorias.append({
                "categoria": row[0],
                "total_transacciones": row[1],
                "unidades_vendidas": row[2],
                "ventas_totales": str(row[3])
            })

        return {
            "total_categorias": len(categorias),
            "categorias": categorias
        }

    except duckdb.Error as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar ventas por categoria"
        ) from error

    finally:
        if con is not None:
            con.close()

# ==========================================
# 8. CONSULTAR EJECUCIONES DEL PIPELINE
# ==========================================

@app.get("/api/pipeline/ejecuciones")
def obtener_ejecuciones_pipeline():

    # Configurar Firestore Emulator local
    os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"

    try:
        # Conectar con Firestore
        db = firestore.Client(
            project="demo-medallion",
            credentials=AnonymousCredentials()
        )

        # Obtener las últimas 20 ejecuciones
        documentos = (
            db.collection("pipeline_executions")
            .order_by(
                "fecha_inicio",
                direction=firestore.Query.DESCENDING
            )
            .limit(20)
            .stream()
        )

        ejecuciones = []

        for documento in documentos:
            datos = documento.to_dict()

            ejecuciones.append({
                "id": documento.id,
                **jsonable_encoder(datos)
            })

        return {
            "total_ejecuciones": len(ejecuciones),
            "ejecuciones": ejecuciones
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar Firestore Emulator"
        ) from error
