# IoT Dispositivos

Este proyecto simula un sistema IoT simple con un sensor y un servidor de lectura.

## Requisitos

- Python 3.12+
- `uv` (recomendado) o `pip`

## Instalación

```bash
uv sync
```

## Ejecución

El sistema consta de dos partes que deben ejecutarse simultáneamente en **terminales separadas**:

### 1. Servidor (Lectura)
Recibe los datos del sensor y los muestra.

```bash
uv run uvicorn lectura:app --port 8000 --reload
```

### 2. Cliente (Sensor)
Genera datos simulados y los envía al servidor.

```bash
uv run python sensor.py
```
