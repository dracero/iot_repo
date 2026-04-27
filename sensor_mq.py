import random
import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# ── Configuración ─────────────────────────────────────────────────────────────

BROKER = "mqtt-dashboard.com"
PORT   = 1883
TOPIC  = "fadena/test"

# ── Sensor virtual ────────────────────────────────────────────────────────────

class SensorVirtual:
    def __init__(self, id, tipo):
        self.id   = id
        self.tipo = tipo

    def leer_valor(self):
        if self.tipo == "temperatura":
            return round(random.uniform(18, 30), 2)
        return random.randint(0, 100)

# ── Main ──────────────────────────────────────────────────────────────────────

sensor = SensorVirtual("S-001", "temperatura")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

print(f"Conectando a broker {BROKER}:{PORT}...")
try:
    client.connect(BROKER, PORT, 60)
except Exception as e:
    print(f"Error conectando al broker: {e}")
    exit(1)

client.loop_start()
print(f"Iniciando publicación en tópico '{TOPIC}'")

try:
    while True:
        valor     = sensor.leer_valor()
        timestamp = datetime.now().isoformat()
        datos     = {"sensor_id": sensor.id, "valor": valor, "timestamp": timestamp}
        payload   = json.dumps(datos)

        info = client.publish(TOPIC, payload)
        info.wait_for_publish()

        print(f"Publicado: {payload}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Deteniendo sensor...")
    client.loop_stop()
    client.disconnect()
