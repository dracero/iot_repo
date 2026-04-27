#!/bin/bash
set -e

echo "=========================================="
echo "  Configuración Automática - IoT Repo"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar Python
echo -e "${YELLOW}[1/5]${NC} Verificando Python 3.12+..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 no está instalado${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION encontrado"

# 2. Instalar uv si no está
echo -e "${YELLOW}[2/5]${NC} Verificando uv..."
if ! command -v uv &> /dev/null; then
    echo "uv no encontrado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo -e "${GREEN}✓${NC} uv instalado"

# 3. Instalar dependencias Python
echo -e "${YELLOW}[3/5]${NC} Instalando dependencias Python..."
uv sync
echo -e "${GREEN}✓${NC} Dependencias instaladas"

# 4. Instalar Mosquitto
echo -e "${YELLOW}[4/5]${NC} Verificando Mosquitto..."
if ! command -v mosquitto &> /dev/null; then
    echo "Mosquitto no encontrado. Instalando..."
    sudo apt update
    sudo apt install -y mosquitto mosquitto-clients openssl
    # Detener servicio del sistema para evitar conflictos
    sudo systemctl stop mosquitto 2>/dev/null || true
    sudo systemctl disable mosquitto 2>/dev/null || true
fi
echo -e "${GREEN}✓${NC} Mosquitto instalado"

# 5. Configurar Mosquitto con TLS
echo -e "${YELLOW}[5/5]${NC} Configurando Mosquitto con TLS..."
chmod +x setup_mosquitto_tls.sh
./setup_mosquitto_tls.sh > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Certificados TLS generados"

echo ""
echo -e "${GREEN}=========================================="
echo "  ✓ Configuración completada exitosamente"
echo "==========================================${NC}"
echo ""
echo "Ejemplos de uso:"
echo ""
echo "  MQTT básico (broker remoto):"
echo "    Terminal 1: uv run python lectura_mq.py"
echo "    Terminal 2: uv run python sensor_mq.py"
echo ""
echo "  MQTT con TLS (broker local):"
echo "    Terminal 1: uv run python sensor_er.py"
echo "    Terminal 2: uv run python lectura_er.py"
echo ""
echo "  HTTP:"
echo "    Terminal 1: uv run uvicorn lectura:app --port 8000"
echo "    Terminal 2: uv run python sensor.py"
echo ""
echo "Ver README.md para más ejemplos y detalles."
