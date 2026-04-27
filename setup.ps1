# Script de configuración automática para Windows
# Requiere PowerShell 5.1+ y permisos de administrador para instalar Mosquitto

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Configuración Automática - IoT Repo" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/4] Verificando Python 3.12+..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
    } else {
        throw "Python no encontrado"
    }
} catch {
    Write-Host "ERROR: Python 3 no está instalado" -ForegroundColor Red
    Write-Host "Descargalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 2. Instalar uv si no está
Write-Host "[2/4] Verificando uv..." -ForegroundColor Yellow
try {
    uv --version | Out-Null
    Write-Host "✓ uv instalado" -ForegroundColor Green
} catch {
    Write-Host "uv no encontrado. Instalando..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "✓ uv instalado" -ForegroundColor Green
}

# 3. Instalar dependencias Python
Write-Host "[3/4] Instalando dependencias Python..." -ForegroundColor Yellow
uv sync
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green

# 4. Verificar Mosquitto
Write-Host "[4/4] Verificando Mosquitto..." -ForegroundColor Yellow
try {
    mosquitto -h | Out-Null
    Write-Host "✓ Mosquitto instalado" -ForegroundColor Green
} catch {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "NOTA: Mosquitto no está instalado." -ForegroundColor Yellow
    Write-Host "Los scripts MQTT básicos (sensor_mq/lectura_mq) funcionan sin Mosquitto." -ForegroundColor Yellow
    Write-Host "Para usar sensor_er/lectura_er con TLS, instalá Mosquitto manualmente:" -ForegroundColor Yellow
    Write-Host "  1. Descargá desde: https://mosquitto.org/download/" -ForegroundColor Cyan
    Write-Host "  2. Instalá el .exe" -ForegroundColor Cyan
    Write-Host "  3. Ejecutá setup_mosquitto_tls.sh en WSL o Git Bash" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✓ Configuración completada" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ejemplos de uso:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  MQTT básico (broker remoto - NO requiere Mosquitto):" -ForegroundColor White
Write-Host "    Terminal 1: uv run python lectura_mq.py" -ForegroundColor Gray
Write-Host "    Terminal 2: uv run python sensor_mq.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  HTTP:" -ForegroundColor White
Write-Host "    Terminal 1: uv run uvicorn lectura:app --port 8000" -ForegroundColor Gray
Write-Host "    Terminal 2: uv run python sensor.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Ver README.md para más ejemplos." -ForegroundColor Cyan
