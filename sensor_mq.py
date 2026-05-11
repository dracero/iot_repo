import random
import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# ── Configuración ─────────────────────────────────────────────────────────────

BROKER_LOCAL  = "localhost"
BROKER_REMOTE = "mqtt-dashboard.com"
PORT          = 1883
TOPIC         = "fadena/test"

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

# Cliente para broker local
client_local = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor-mq-local")
# Cliente para broker remoto
client_remote = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor-mq-remote")

print(f"Conectando a broker local {BROKER_LOCAL}:{PORT}...")
try:
    client_local.connect(BROKER_LOCAL, PORT, 60)
    client_local.loop_start()
    print(f"✓ Conectado a {BROKER_LOCAL}")
except Exception as e:
    print(f"⚠ No se pudo conectar a broker local: {e}")
    client_local = None

print(f"Conectando a broker remoto {BROKER_REMOTE}:{PORT}...")
try:
    client_remote.connect(BROKER_REMOTE, PORT, 60)
    client_remote.loop_start()
    print(f"✓ Conectado a {BROKER_REMOTE}")
except Exception as e:
    print(f"⚠ No se pudo conectar a broker remoto: {e}")
    client_remote = None

if not client_local and not client_remote:
    print("ERROR: No se pudo conectar a ningún broker")
    exit(1)

print(f"Iniciando publicación en tópico '{TOPIC}'")

try:
    while True:
        valor     = sensor.leer_valor()
        timestamp = datetime.now().isoformat()
        datos     = {"sensor_id": sensor.id, "valor": valor, "timestamp": timestamp}
        payload   = json.dumps(datos)

        # Publicar en broker local
        if client_local:
            info = client_local.publish(TOPIC, payload)
            info.wait_for_publish()
            print(f"[LOCAL] Publicado: {payload}")

        # Publicar en broker remoto
        if client_remote:
            info = client_remote.publish(TOPIC, payload)
            info.wait_for_publish()
            print(f"[REMOTO] Publicado: {payload}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Deteniendo sensor...")
    if client_local:
        client_local.loop_stop()
        client_local.disconnect()
    if client_remote:
        client_remote.loop_stop()
        client_remote.disconnect()
