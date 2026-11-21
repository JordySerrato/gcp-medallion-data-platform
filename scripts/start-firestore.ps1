
# ==========================================
# INICIAR FIRESTORE EMULATOR
# ==========================================

$ErrorActionPreference = "Stop"

# 1. Ubicar la raiz del proyecto
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJECT_ROOT

# 2. Directorios de respaldos
$BACKUP_DIR = Join-Path $PROJECT_ROOT "data\firestore-export"
$CURRENT_DIR = Join-Path $BACKUP_DIR "current"
$SNAPSHOT_DIR = Join-Path $BACKUP_DIR "snapshot-20261121"

New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null

# 3. Configurar Firebase CLI
$FIREBASE_ARGS = @(
    "emulators:start"
    "--only", "firestore"
    "--project", "demo-medallion"
    "--export-on-exit", $CURRENT_DIR
)

# 4. Seleccionar el respaldo disponible
$IMPORT_DIR = $null

if (Test-Path (Join-Path $CURRENT_DIR "firebase-export-metadata.json")) {
    $IMPORT_DIR = $CURRENT_DIR
}
elseif (Test-Path (Join-Path $SNAPSHOT_DIR "firebase-export-metadata.json")) {
    $IMPORT_DIR = $SNAPSHOT_DIR
}
elseif (Test-Path (Join-Path $BACKUP_DIR "firebase-export-metadata.json")) {
    $IMPORT_DIR = $BACKUP_DIR
}

# 5. Importar datos si existe un respaldo
if ($IMPORT_DIR) {
    Write-Host "Respaldo encontrado: $IMPORT_DIR"
    $FIREBASE_ARGS += @("--import", $IMPORT_DIR)
}
else {
    Write-Host "No existe respaldo. Firestore iniciara vacio."
}

# 6. Iniciar emulador
Write-Host "Iniciando Firestore Emulator..."

& firebase @FIREBASE_ARGS
