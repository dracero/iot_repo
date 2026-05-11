import json
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import paho.mqtt.client as mqtt
import threading

class Lectura(BaseModel):
    sensor_id: str
    valor: float
    timestamp: Optional[str] = None

# Configuración MQTT
BROKER_LOCAL  = "localhost"
BROKER_REMOTE = "broker.hivemq.com"
PORT          = 8883
TOPIC         = "fadena/test"
CA_CERT_LOCAL = os.path.expanduser("~/.mosquitto/certs/ca.crt")

# Variable global para almacenar el último dato recibido
ultimo_dato: Optional[Lectura] = None
mensajes_recibidos: list = []

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
        print(f"[{ultimo_dato.timestamp}] Procesado: sensor={ultimo_dato.sensor_id}, valor={ultimo_dato.valor}")
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# Inicializar clientes MQTT con TLS
mqtt_client_local = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"lectura-er-local-{os.getpid()}", userdata={'broker_type': 'local'})
mqtt_client_local.tls_set(ca_certs=CA_CERT_LOCAL)
mqtt_client_local.on_connect = on_connect_local
mqtt_client_local.on_message = on_message

mqtt_client_remote = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"lectura-er-remote-{os.getpid()}", userdata={'broker_type': 'remoto'})
mqtt_client_remote.tls_set()  # Usa certificados del sistema
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_thread_local = threading.Thread(target=start_mqtt_local, daemon=True)
    mqtt_thread_local.start()
    mqtt_thread_remote = threading.Thread(target=start_mqtt_remote, daemon=True)
    mqtt_thread_remote.start()
    print("Clientes MQTT iniciados en segundo plano (local TLS + remoto TLS)")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/telemetria")
async def leer_dato_actual():
    """Devuelve el último dato recibido."""
    return {"status": "online", "ultimo_dato": ultimo_dato}

@app.get("/telemetria/historial")
async def leer_historial():
    """Devuelve los últimos 10 mensajes recibidos."""
    return {"status": "online", "mensajes": mensajes_recibidos}

@app.get("/")
async def home():
    return {
        "message": "Servidor de lectura para sensor_er.py activo",
        "brokers": {
            "local": f"{BROKER_LOCAL}:{PORT}",
            "remoto": f"{BROKER_REMOTE}:{PORT}"
        },
        "endpoints": {
            "/telemetria": "Último dato recibido",
            "/telemetria/historial": "Últimos 10 mensajes"
        }
    }

if __name__ == "__main__":
    print("Iniciando servidor de lectura para sensor_er en http://localhost:8002...")
    print(f"Conectando a broker local: {BROKER_LOCAL}:{PORT} (TLS)")
    print(f"Conectando a broker remoto: {BROKER_REMOTE}:{PORT} (TLS)")
    uvicorn.run(app, host="0.0.0.0", port=8002)
