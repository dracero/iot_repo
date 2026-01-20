import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import paho.mqtt.client as mqtt
import threading

class Lectura(BaseModel):
    sensor_id: str
    valor: float
    timestamp: Optional[str] = None

# Configuración MQTT (mismo broker y tópico que sensor_er.py)
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/telemetria"

app = FastAPI()

# Variable global para almacenar el último dato recibido
ultimo_dato: Optional[Lectura] = None
mensajes_recibidos: list = []

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Conectado al broker MQTT con código: {rc}")
    client.subscribe(TOPIC)
    print(f"Suscrito al tópico: {TOPIC}")

def on_message(client, userdata, msg):
    global ultimo_dato, mensajes_recibidos
    payload = msg.payload.decode()
    print(f"Recibido mensaje en {msg.topic}: {payload}")
    try:
        data_dict = json.loads(payload)
        ultimo_dato = Lectura(**data_dict)
        # Guardar últimos 10 mensajes
        mensajes_recibidos.append(ultimo_dato.model_dump())
        if len(mensajes_recibidos) > 10:
            mensajes_recibidos.pop(0)
        print(f"[{ultimo_dato.timestamp}] Procesado: sensor={ultimo_dato.sensor_id}, valor={ultimo_dato.valor}")
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# Inicializar cliente MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    """Inicia el cliente MQTT en un hilo separado."""
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"Error conectando al broker MQTT: {e}")

@app.on_event("startup")
async def startup_event():
    """Inicia el cliente MQTT cuando arranca FastAPI."""
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    print("Cliente MQTT iniciado en segundo plano")

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
        "endpoints": {
            "/telemetria": "Último dato recibido",
            "/telemetria/historial": "Últimos 10 mensajes"
        }
    }

if __name__ == "__main__":
    print("Iniciando servidor de lectura para sensor_er en http://localhost:8002...")
    print(f"Conectando a broker {BROKER}:{PORT}, tópico: {TOPIC}")
    uvicorn.run(app, host="0.0.0.0", port=8002)
