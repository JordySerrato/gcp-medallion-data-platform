
# ==========================================
# INICIAR SERVICIOS DOCKER DEL PROYECTO
# ==========================================

$ErrorActionPreference = "Stop"

# Ubicar la raiz del proyecto
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

Write-Host "=================================="
Write-Host " GCP MEDALLION DATA PLATFORM"
Write-Host "=================================="

# Comprobar que Docker esta disponible
docker info *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Docker no esta disponible. Inicia Docker Desktop."
}

# Iniciar el emulador GCS
Write-Host "Iniciando GCS Emulator..."

docker compose up -d gcs-emulator

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo iniciar GCS Emulator."
}

Write-Host "GCS Emulator iniciado."

# ==========================================
# EJECUTAR PIPELINE MEDALLION
# ==========================================

Write-Host ""

# ==========================================
# VERIFICAR FIRESTORE EMULATOR
# ==========================================

Write-Host "Verificando Firestore Emulator..."

$FIRESTORE_OK = Test-NetConnection `
    -ComputerName "127.0.0.1" `
    -Port 8080 `
    -InformationLevel Quiet `
    -WarningAction SilentlyContinue

if (-not $FIRESTORE_OK) {
    throw "Firestore Emulator no esta activo. Ejecuta .\scripts\start-firestore.ps1 en otra terminal."
}

Write-Host "Firestore Emulator disponible."

Write-Host "Ejecutando pipeline Medallion..."

# Utilizar Python del entorno virtual
$PYTHON = Join-Path $PROJECT_ROOT ".venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON)) {
    throw "No se encontro Python en .venv. Debes preparar el entorno virtual."
}

# Ejecutar orquestador
& $PYTHON (Join-Path $PROJECT_ROOT "pipeline.py")

if ($LASTEXITCODE -ne 0) {
    throw "El pipeline Medallion termino con errores."
}

Write-Host "Pipeline Medallion completado correctamente."


# ==========================================
# INICIAR BACKEND Y FRONTEND
# ==========================================

Write-Host ""
Write-Host "Iniciando Backend FastAPI y Frontend React..."

# Construir e iniciar los servicios
docker compose up -d --build backend frontend

if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron iniciar Backend y Frontend."
}

Write-Host ""
Write-Host "=================================="
Write-Host " SERVICIOS DOCKER INICIADOS"
Write-Host "=================================="
Write-Host "Dashboard: http://127.0.0.1:8081"
Write-Host "Backend:   http://127.0.0.1:8001"
Write-Host "API Docs:  http://127.0.0.1:8001/docs"
