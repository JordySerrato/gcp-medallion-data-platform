
import os

from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

# 1. Configurar la dirección del emulador local
os.environ["STORAGE_EMULATOR_HOST"] = "http://127.0.0.1:4444"

# 2. Crear el cliente de Google Cloud Storage
client = storage.Client(
    project="local-project",
    credentials=AnonymousCredentials()
)

# 3. Conectarse al bucket Landing
bucket = client.get_bucket("medallion-landing")

# 4. Mostrar el resultado
print("Conexión exitosa con Google Cloud Storage Emulator")
print(f"Bucket encontrado: {bucket.name}")
