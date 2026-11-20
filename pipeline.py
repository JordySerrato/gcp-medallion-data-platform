
import os
import subprocess
import sys

from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials

# ==========================================
# 1. CONFIGURACIÓN LOCAL
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"

PROJECT_ID = "demo-medallion"
PIPELINE_NAME = "ventas_medallion"

# ==========================================
# 2. CONEXIÓN A FIRESTORE
# ==========================================

db = firestore.Client(
    project=PROJECT_ID,
    credentials=AnonymousCredentials()
)

# ==========================================
# 3. ETAPAS DEL PIPELINE
# ==========================================

PIPELINE = [
    (
        "external_to_landing",
        "External to Landing",
        "ingestion/external_to_landing/upload_to_landing.py"
    ),
    (
        "landing_to_bronze",
        "Landing to Bronze",
        "ingestion/external_to_bronze/landing_to_bronze.py"
    ),
    (
        "bronze_to_silver",
        "Bronze to Silver",
        "warehouse/silver/bronze_to_silver.py"
    ),
    (
        "silver_to_gold",
        "Silver to Gold",
        "warehouse/gold/silver_to_gold.py"
    )
]


def fecha_actual():
    return datetime.now(timezone.utc)


# ==========================================
# 4. EJECUTAR PIPELINE
# ==========================================

def ejecutar_pipeline():

    ejecucion_id = str(uuid4())

    documento = db.collection(
        "pipeline_executions"
    ).document(ejecucion_id)

    # Registrar inicio
    documento.set({
        "pipeline": PIPELINE_NAME,
        "estado": "RUNNING",
        "fecha_inicio": fecha_actual(),
        "fecha_fin": None,
        "etapa_actual": None,
        "etapas": {},
        "error": None
    })

    print("INICIANDO PIPELINE MEDALLION")
    print(f"Ejecucion ID: {ejecucion_id}")

    for codigo, nombre, ruta in PIPELINE:

        print(f"\nEjecutando: {nombre}", flush=True)

        documento.update({
            "etapa_actual": codigo,
            f"etapas.{codigo}": {
                "estado": "RUNNING",
                "fecha_inicio": fecha_actual()
            }
        })

        archivo = BASE_DIR / ruta

        try:
            subprocess.run(
                [sys.executable, str(archivo)],
                cwd=BASE_DIR,
                check=True
            )

        except subprocess.CalledProcessError as error:

            documento.update({
                "estado": "FAILED",
                "fecha_fin": fecha_actual(),
                "error": f"{nombre}: codigo {error.returncode}",
                f"etapas.{codigo}.estado": "FAILED",
                f"etapas.{codigo}.fecha_fin": fecha_actual()
            })

            print(f"ERROR en etapa: {nombre}")
            raise

        documento.update({
            f"etapas.{codigo}.estado": "COMPLETED",
            f"etapas.{codigo}.fecha_fin": fecha_actual()
        })

        print(f"Completado: {nombre}", flush=True)

    # Registrar finalización
    documento.update({
        "estado": "COMPLETED",
        "fecha_fin": fecha_actual(),
        "etapa_actual": None
    })

    print("\nPIPELINE MEDALLION COMPLETADO")
    print(f"Registro Firestore: {ejecucion_id}")


if __name__ == "__main__":
    try:
        ejecutar_pipeline()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode or 1)
