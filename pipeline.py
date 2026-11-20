
import subprocess
import sys
from pathlib import Path

# Raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Procesos en orden de ejecución
PIPELINE = [
    (
        "External to Landing",
        "ingestion/external_to_landing/upload_to_landing.py"
    ),
    (
        "Landing to Bronze",
        "ingestion/external_to_bronze/landing_to_bronze.py"
    ),
    (
        "Bronze to Silver",
        "warehouse/silver/bronze_to_silver.py"
    ),
    (
        "Silver to Gold",
        "warehouse/gold/silver_to_gold.py"
    )
]


def ejecutar_pipeline():
    print("INICIANDO PIPELINE MEDALLION")

    for nombre, ruta in PIPELINE:
        print(f"\nEjecutando: {nombre}", flush=True)

        archivo = BASE_DIR / ruta

        subprocess.run(
            [sys.executable, str(archivo)],
            cwd=BASE_DIR,
            check=True
        )

        print(f"Completado: {nombre}", flush=True)

    print("\nPIPELINE MEDALLION COMPLETADO")


if __name__ == "__main__":
    try:
        ejecutar_pipeline()
    except subprocess.CalledProcessError as error:
        print(
            f"\nPipeline detenido. Código de error: "
            f"{error.returncode}"
        )
        sys.exit(1)
