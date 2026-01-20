import random
import time
import json
import ssl
import os
from datetime import datetime
import paho.mqtt.client as mqtt

class SensorVirtual:
    def __init__(self, id, tipo):
        self.id = id
        self.tipo = tipo
    
    def leer_valor(self):
        if self.tipo == "temperatura":
            return round(random.uniform(18, 30), 2)
        return random.randint(0, 100)

sensor = SensorVirtual("S-001", "temperatura")
broker_address = "test.mosquitto.org"
topic = "iot/telemetria"
ca_cert = os.path.join(os.path.dirname(__file__), "certs", "mosquitto.org.crt")

print(f"Conectando al broker {broker_address} con TLS...")
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.tls_set(ca_certs=ca_cert)  # Habilitar TLS con certificado CA local
try:
    client.connect(broker_address, 8883, 60)  # Puerto TLS
except Exception as e:
    print(f"Error conectando al broker: {e}")
    exit(1)

client.loop_start()

print(f"Iniciando publicación en topico '{topic}'")

try:
    while True:
        valor = sensor.leer_valor()
        timestamp = datetime.now().isoformat()
        datos = {"sensor_id": sensor.id, "valor": valor, "timestamp": timestamp}
        payload = json.dumps(datos)
        
        info = client.publish(topic, payload)
        info.wait_for_publish()
        
        print(f"Publicado: {payload}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Deteniendo sensor...")
    client.loop_stop()
    client.disconnect()
