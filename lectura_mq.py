import json
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

# ── Estado global ─────────────────────────────────────────────────────────────

ultimo_dato: Optional[Lectura] = None
mensajes_recibidos: list = []

# ── Callbacks MQTT ────────────────────────────────────────────────────────────

def on_connect_local(client, userdata, flags, reason_code, properties):
    print(f"Conectado al broker LOCAL con código: {reason_code}")
    client.subscribe(TOPIC)
    print(f"Suscrito al tópico: {TOPIC} (local)")

def on_connect_remote(client, userdata, flags, reason_code, properties):
    print(f"Conectado al broker REMOTO con código: {reason_code}")
    client.subscribe(TOPIC)
    print(f"Suscrito al tópico: {TOPIC} (remoto)")

def on_message(client, userdata, msg):
    global ultimo_dato, mensajes_recibidos
    payload = msg.payload.decode()
    broker_type = userdata.get('broker_type', 'unknown')
    print(f"[{broker_type.upper()}] Recibido en {msg.topic}: {payload}")
    try:
        data_dict = json.loads(payload)
        ultimo_dato = Lectura(**data_dict)
        mensajes_recibidos.append(ultimo_dato.model_dump())
        if len(mensajes_recibidos) > 10:
            mensajes_recibidos.pop(0)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# ── Clientes MQTT en hilos separados ──────────────────────────────────────────

mqtt_client_local = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lectura-mq-local", userdata={'broker_type': 'local'})
mqtt_client_local.on_connect = on_connect_local
mqtt_client_local.on_message = on_message

mqtt_client_remote = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lectura-mq-remote", userdata={'broker_type': 'remoto'})
mqtt_client_remote.on_connect = on_connect_remote
mqtt_client_remote.on_message = on_message

def start_mqtt_local():
    try:
        mqtt_client_local.connect(BROKER_LOCAL, PORT, 60)
        mqtt_client_local.loop_forever()
    except Exception as e:
        print(f"Error conectando al broker LOCAL: {e}")

def start_mqtt_remote():
    try:
        mqtt_client_remote.connect(BROKER_REMOTE, PORT, 60)
        mqtt_client_remote.loop_forever()
    except Exception as e:
        print(f"Error conectando al broker REMOTO: {e}")

# ── FastAPI ───────────────────────────────────────────────────────────────────

app = FastAPI(title="Lector MQTT")

@app.on_event("startup")
async def startup_event():
    thread_local = threading.Thread(target=start_mqtt_local, daemon=True)
    thread_local.start()
    thread_remote = threading.Thread(target=start_mqtt_remote, daemon=True)
    thread_remote.start()
    print("Clientes MQTT iniciados en segundo plano (local + remoto)")

@app.get("/")
async def home():
    return {
        "message": "Lector MQTT activo", 
        "brokers": {
            "local": BROKER_LOCAL,
            "remoto": BROKER_REMOTE
        },
        "topic": TOPIC
    }

@app.get("/telemetria")
async def leer_dato_actual():
    return {"status": "online", "ultimo_dato": ultimo_dato}

@app.get("/telemetria/historial")
async def leer_historial():
    return {"status": "online", "mensajes": mensajes_recibidos}

if __name__ == "__main__":
    print("Iniciando servidor de lectura MQTT en http://localhost:8001...")
    print(f"Escuchando en broker local: {BROKER_LOCAL}:{PORT}")
    print(f"Escuchando en broker remoto: {BROKER_REMOTE}:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
