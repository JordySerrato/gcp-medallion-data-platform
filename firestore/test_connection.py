
import os
from datetime import datetime, timezone

from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore

# ==========================================
# 1. CONFIGURACIÓN LOCAL
# ==========================================

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"

PROJECT_ID = "demo-medallion"

# ==========================================
# 2. CONEXIÓN A FIRESTORE
# ==========================================

client = firestore.Client(
    project=PROJECT_ID,
    credentials=AnonymousCredentials()
)

# ==========================================
# 3. CREAR DOCUMENTO DE PRUEBA
# ==========================================

documento = client.collection(
    "pipeline_executions"
).document("test_connection")

documento.set({
    "pipeline": "ventas_medallion",
    "estado": "TEST",
    "mensaje": "Conexion desde Python exitosa",
    "fecha_registro": datetime.now(timezone.utc)
})

# ==========================================
# 4. VERIFICAR DOCUMENTO
# ==========================================

resultado = documento.get()

if resultado.exists:
    print("Conexion exitosa con Firestore Emulator")
    print(f"Documento encontrado: {resultado.id}")
    print(f"Datos: {resultado.to_dict()}")
else:
    print("No se encontro el documento")
