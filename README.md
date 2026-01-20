# IoT Dispositivos

Este proyecto simula un sistema IoT simple con diferentes protocolos de comunicación: HTTP, MQTT, WebSocket y CoAP.

## Requisitos

- Python 3.12+
- `uv` (recomendado) o `pip`

## Instalación

```bash
uv sync
```

## Ejecución

El sistema contiene varios ejemplos de comunicación IoT. Cada protocolo requiere ejecutar los scripts en **terminales separadas** y en el orden indicado.

---

### HTTP (Simulación básica)

Estos scripts simulan comunicación HTTP entre un sensor y un servidor de lectura.

**1. Primero - Servidor (Lectura):**
```bash
uv run uvicorn lectura:app --port 8000 --reload
```

**2. Después - Cliente (Sensor):**
```bash
uv run python sensor.py
```

---

### MQTT (Message Queue Telemetry Transport)

Estos scripts demuestran el protocolo MQTT para mensajería IoT.

**1. Primero - Suscriptor (Lectura):**
```bash
uv run python lectura_mq.py
```

**2. Después - Publicador (Sensor):**
```bash
uv run python sensor_mq.py
```

---

### MQTT con Simulación de Errores

Estos scripts demuestran MQTT con lógica de reintentos y simulación de errores de red/hardware.

**1. Primero - Suscriptor (Lectura):**
```bash
uv run python lectura_er.py
```

**2. Después - Publicador (Sensor con errores simulados):**
```bash
uv run python sensor_er.py
```

El servidor estará en http://localhost:8002 con endpoints:
- `/telemetria` - Último dato recibido
- `/telemetria/historial` - Últimos 10 mensajes

---

### WebSocket

Estos scripts demuestran comunicación bidireccional en tiempo real mediante WebSocket.

**1. Primero - Servidor:**
```bash
uv run python ws_server.py
```

**2. Después - Cliente:**
```bash
uv run python ws_client.py
```

---

### CoAP (Constrained Application Protocol)

Estos scripts demuestran el protocolo CoAP diseñado para dispositivos IoT con recursos limitados.

**1. Primero - Servidor:**
```bash
uv run python coap_server.py
```

**2. Después - Cliente:**
```bash
uv run python coap_client.py
```

---

### ESP32 con Wokwi

El script `esp32_mqtt.py` se utiliza para conectarse a la simulación de ESP32 en Wokwi.

```bash
uv run python esp32_mqtt.py
```

---

### MQTT con HiveMQ (Broker Público)

El script `sensor_mq_pub.py` publica datos al broker público HiveMQ. Para leer los mensajes, debes usar el cliente web de HiveMQ para suscribirte al tópico correspondiente.

**Publicador:**
```bash
uv run python sensor_mq_pub.py
```

**Lector:** Usa el [cliente web de HiveMQ](https://www.hivemq.com/demos/websocket-client/) para suscribirte y leer los mensajes del tópico.

---

## Captura con Wireshark

Para analizar el tráfico de cada protocolo, abre Wireshark en la interfaz `lo` (loopback) para comunicación local o `any` para capturar todo el tráfico.

### Filtros por Protocolo

| Protocolo | Filtro Wireshark | Puerto |
|-----------|------------------|--------|
| **HTTP** (lectura + sensor) | `tcp.port == 8000` | 8000 |
| **MQTT** (lectura_mq + sensor_mq) | `mqtt` o `tcp.port == 8883` | 8883 (TLS) |
| **MQTT** (lectura_er + sensor_er) | `mqtt` o `tcp.port == 1883` | 1883 |
| **WebSocket** (ws_server + ws_client) | `websocket` o `tcp.port == 8000` | 8000 |
| **CoAP** (coap_server + coap_client) | `coap` o `udp.port == 5683` | 5683 |

### Instrucciones de Captura

1. **Abrir Wireshark** y seleccionar la interfaz:
   - `lo` o `Loopback` para tráfico local (localhost)
   - `any` para capturar todo el tráfico

2. **Aplicar el filtro** correspondiente en la barra de filtros

3. **Iniciar captura** (botón azul o Ctrl+E)

4. **Ejecutar los scripts** cliente-servidor en terminales separadas

5. **Detener captura** y analizar los paquetes

### Ejemplo: Capturar WebSocket

```bash
# En Wireshark: filtro "tcp.port == 8000"
# Terminal 1:
uv run python ws_server.py
# Terminal 2:
uv run python ws_client.py
```

### Ejemplo: Capturar CoAP (UDP)

```bash
# En Wireshark: filtro "coap" o "udp.port == 5683"
# Terminal 1:
uv run python coap_server.py
# Terminal 2:
uv run python coap_client.py
```
