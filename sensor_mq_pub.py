import asyncio
import random
import json
import uvicorn
from datetime import datetime
from fastapi import FastAPI
from fastapi_mqtt import FastMQTT, MQTTConfig

# Configuración del Broker MQTT
# Host: broker.hivemq.com
# Topic: fadena/test
mqtt_config = MQTTConfig(
    host="broker.hivemq.com",
    port=1883,
    keepalive=60
)

app = FastAPI(title="Simulador de Sensor MQTT")
fast_mqtt = FastMQTT(config=mqtt_config)
fast_mqtt.init_app(app)

# Estado del sensor
sensor_data = {
    "sensor_id": "TEMP-SIM-001",
    "tipo": "temperatura",
    "valor": 25.0,
    "unidad": "Celsius",
    "timestamp": ""
}

async def simulate_sensor_readings():
    """ Tarea en segundo plano para simular y enviar datos """
    while True:
        # Simular variación de temperatura
        sensor_data["valor"] = round(random.uniform(20.0, 30.0), 2)
        sensor_data["timestamp"] = datetime.now().isoformat()
        
        payload = json.dumps(sensor_data)
        
        # Publicar en el tópico solicitado
        fast_mqtt.publish("fadena/test", payload)
        
        print(f"Publicado en fadena/test: {payload}")
        
        # Esperar 5 segundos antes de la próxima lectura
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    # Iniciar la tarea de simulación al arrancar la app
    asyncio.create_task(simulate_sensor_readings())

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    print(f"Conectado al broker MQTT: {mqtt_config.host}")

@app.get("/")
async def root():
    return {
        "message": "Simulador de Sensor MQTT iniciado",
        "topic": "fadena/test",
        "broker": mqtt_config.host,
        "current_status": sensor_data
    }

@app.get("/status")
async def get_status():
    return sensor_data

if __name__ == "__main__":
    # Usamos el puerto 8002 para evitar conflictos con otros sensores/lectores
    print("Iniciando FastAPI en http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
