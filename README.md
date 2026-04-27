# IoT Dispositivos

Este proyecto simula un sistema IoT simple con diferentes protocolos de comunicación: HTTP, MQTT, WebSocket y CoAP.

## Requisitos

- Python 3.12+
- `uv` (recomendado) o `pip`
- Mosquitto (para `lectura_er` y `sensor_er`)

## Instalación

```bash
uv sync
```

### Instalar Mosquitto (broker MQTT local)

Requerido para `sensor_er.py` y `lectura_er.py`. Solo necesitás instalarlo — `sensor_er.py` lo levanta automáticamente al ejecutarse.

```bash
sudo apt update && sudo apt install -y mosquitto mosquitto-clients
```

Verificar que está instalado:

```bash
which mosquitto
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

Estos scripts demuestran el protocolo MQTT para mensajería IoT usando el broker público **mqtt-dashboard.com** en el puerto **1883**.

El broker es compartido con el ESP32 en Wokwi, por lo que `lectura_mq.py` también recibe los datos del ESP32.

**1. Primero - Suscriptor (Lectura):**
```bash
uv run python lectura_mq.py
```
Servidor en http://localhost:8001 con endpoints:
- `/telemetria` - Último dato recibido
- `/telemetria/historial` - Últimos 10 mensajes

**2. Después - Publicador (Sensor):**
```bash
uv run python sensor_mq.py
```

---

### MQTT con Simulación de Errores

Estos scripts demuestran MQTT con lógica de reintentos y simulación de errores de red/hardware usando **Mosquitto local** en el puerto **1883**.

> Requiere Mosquitto instalado (ver sección de instalación arriba).
> `sensor_er.py` levanta Mosquitto automáticamente al ejecutarse. Iniciá siempre `sensor_er.py` antes que `lectura_er.py`.

**1. Primero - Publicador (levanta Mosquitto y publica datos):**
```bash
uv run python sensor_er.py
```

**2. Después - Suscriptor (Lectura):**
```bash
uv run python lectura_er.py
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

El script `esp32_mqtt.py` corre en el simulador [Wokwi](https://wokwi.com) sobre un ESP32 con sensor DHT22. Publica datos de temperatura y humedad en el broker **mqtt-dashboard.com:1883**, tópico `fadena/test`.

Para ver los datos en tu PC, corré `lectura_mq.py` que escucha el mismo broker y tópico.

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
| **MQTT** (lectura_mq + sensor_mq + ESP32) | `tcp.port == 1883` | 1883 (mqtt-dashboard.com) |
| **MQTT con errores** (lectura_er + sensor_er) | `tcp.port == 1883` | 1883 (Mosquitto local) |
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
