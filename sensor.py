import random
import time

import requests

class SensorVirtual:
    def __init__(self, id, tipo):
        self.id = id
        self.tipo = tipo
    
    def leer_valor(self):
        if self.tipo == "temperatura":
            return round(random.uniform(18, 30), 2)
        return random.randint(0, 100)

sensor = SensorVirtual("S-001", "temperatura")

while True:
    valor = sensor.leer_valor()
    datos = {"sensor_id": sensor.id, "valor": valor}
    try:
        response = requests.post("http://localhost:8000/telemetria", json=datos)
        print(f"Enviado: {datos}, Respuesta: {response.status_code}")
    except Exception as e:
        print(f"Error enviando datos: {e}")
        print("HINT: Asegúrate de que lectura.py esté corriendo en otra terminal (uv run uvicorn lectura:app --port 8000)")
    time.sleep(2)