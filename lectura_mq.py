import uvicorn
from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig
from pydantic import BaseModel
from typing import Optional

class Lectura(BaseModel):
    sensor_id: str
    valor: float

# Configuración MQTT usando test.mosquitto.org
mqtt_config = MQTTConfig(
    host="test.mosquitto.org",
    port=1883,
    keepalive=60,
)

app = FastAPI()
fast_mqtt = FastMQTT(config=mqtt_config)

fast_mqtt.init_app(app)

# Variable global para almacenar el último dato recibido
ultimo_dato: Optional[Lectura] = None

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    # client.subscribe("/mqtt") #  subscribing mqtt topic
    print("Conectado al broker MQTT: ", client, flags, rc, properties)

@fast_mqtt.subscribe("iot/telemetria")
async def recibir_telemetria(client, topic, payload, qos, properties):
    global ultimo_dato
    print(f"Recibido mensaje en {topic}: {payload.decode()}")
    try:
        # Asumimos que el payload es JSON válido que coincide con el modelo
        import json
        data_dict = json.loads(payload.decode())
        ultimo_dato = Lectura(**data_dict)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

@app.get("/telemetria")
async def leer_dato_actual():
    return {"status": "online", "ultimo_dato": ultimo_dato}

@app.get("/")
async def home():
    return {"message": "Servidor MQTT activo. Ve a /telemetria para ver los datos."}

if __name__ == "__main__":
    print("Iniciando servidor de lectura MQTT en http://localhost:8000...")
    # Usamos puerto 8001 para evitar conflicto si lectura.py sigue corriendo en 8000
    uvicorn.run(app, host="0.0.0.0", port=8001)
