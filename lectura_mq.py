import json
import socket
import threading
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import paho.mqtt.client as mqtt

# ── Modelo ────────────────────────────────────────────────────────────────────

class Lectura(BaseModel):
    # Campos del ESP32 (esp32_mqtt.py)
    temp: Optional[float] = None
    humidity: Optional[float] = None
    client_id: Optional[str] = None
    # Campos de sensores Python (sensor_mq_pub.py, sensor_mq.py)
    sensor_id: Optional[str] = None
    valor: Optional[float] = None
    timestamp: Optional[str] = None

# ── Configuración ─────────────────────────────────────────────────────────────

BROKER_LOCAL  = "localhost"
BROKER_REMOTE = "mqtt-dashboard.com"
PORT          = 1883
TOPIC         = "fadena/test"

def _broker_running(host: str) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, PORT)) == 0

BROKER = BROKER_REMOTE  # Siempre usar broker remoto para recibir del ESP32
print(f"Usando broker: {BROKER}")

# ── Estado global ─────────────────────────────────────────────────────────────

ultimo_dato: Optional[Lectura] = None
mensajes_recibidos: list = []

# ── Callbacks MQTT ────────────────────────────────────────────────────────────

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Conectado al broker MQTT {BROKER} con código: {rc}")
    client.subscribe(TOPIC)
    print(f"Suscrito al tópico: {TOPIC}")

def on_message(client, userdata, msg):
    global ultimo_dato, mensajes_recibidos
    payload = msg.payload.decode()
    print(f"Recibido en {msg.topic}: {payload}")
    try:
        data_dict = json.loads(payload)
        ultimo_dato = Lectura(**data_dict)
        mensajes_recibidos.append(ultimo_dato.model_dump())
        if len(mensajes_recibidos) > 10:
            mensajes_recibidos.pop(0)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# ── Cliente MQTT en hilo separado ─────────────────────────────────────────────

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"Error conectando al broker MQTT: {e}")

# ── FastAPI ───────────────────────────────────────────────────────────────────

app = FastAPI(title="Lector MQTT")

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=start_mqtt, daemon=True)
    thread.start()
    print("Cliente MQTT iniciado en segundo plano")

@app.get("/")
async def home():
    return {"message": "Lector MQTT activo", "broker": BROKER, "topic": TOPIC}

@app.get("/telemetria")
async def leer_dato_actual():
    return {"status": "online", "ultimo_dato": ultimo_dato}

@app.get("/telemetria/historial")
async def leer_historial():
    return {"status": "online", "mensajes": mensajes_recibidos}

if __name__ == "__main__":
    print("Iniciando servidor de lectura MQTT en http://localhost:8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
