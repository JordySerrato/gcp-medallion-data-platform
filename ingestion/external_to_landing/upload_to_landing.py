
import os
from pathlib import Path

from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

# 1. CONFIGURACIÓN DEL EMULADOR
os.environ["STORAGE_EMULATOR_HOST"] = "http://127.0.0.1:4444"

PROJECT_ID = "local-project"
BUCKET_NAME = "medallion-landing"

# 2. UBICACIÓN DEL ARCHIVO CSV
BASE_DIR = Path(__file__).resolve().parents[2]
FILE_PATH = BASE_DIR / "data" / "samples" / "ventas.csv"

# 3. NOMBRE DEL OBJETO EN CLOUD STORAGE
DESTINATION_BLOB = "ventas/2026/11/20/ventas.csv"


def upload_to_landing():
    # Verificar que exista el archivo local
    if not FILE_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo: {FILE_PATH}"
        )

    # Crear cliente de Cloud Storage
    client = storage.Client(
        project=PROJECT_ID,
        credentials=AnonymousCredentials()
    )

    # Obtener referencia al bucket
    bucket = client.bucket(BUCKET_NAME)

    # Crear referencia al objeto
    blob = bucket.blob(DESTINATION_BLOB)

    # Subir archivo CSV
    blob.upload_from_filename(
        str(FILE_PATH),
        content_type="text/csv"
    )

    print("Archivo cargado correctamente a Landing")
    print(f"Origen: {FILE_PATH}")
    print(f"Destino: gs://{BUCKET_NAME}/{DESTINATION_BLOB}")


if __name__ == "__main__":
    upload_to_landing()
