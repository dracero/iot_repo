import asyncio
import json
import random
import subprocess
import socket
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# ── Configuración ─────────────────────────────────────────────────────────────

BROKER_LOCAL  = "localhost"
BROKER_REMOTE = "broker.hivemq.com"
PORT          = 8883
TOPIC         = "fadena/test"
CA_CERT_LOCAL = os.path.expanduser("~/.mosquitto/certs/ca.crt")

# ── Mosquitto local ───────────────────────────────────────────────────────────

def _broker_running() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", 8883)) == 0

def start_broker():
    if _broker_running():
        print("Broker Mosquitto TLS ya está corriendo.")
        return None

    mosquitto_path = subprocess.run(
        ["which", "mosquitto"], capture_output=True, text=True
    ).stdout.strip()

    if not mosquitto_path:
        print("ERROR: Mosquitto no está instalado. Instalalo con: sudo apt install mosquitto")
        exit(1)

    conf_file = os.path.expanduser("~/.mosquitto/mosquitto.conf")
    if not os.path.exists(conf_file):
        print(f"ERROR: Archivo de configuración no encontrado: {conf_file}")
        print("Ejecutá primero: ./setup_mosquitto_tls.sh")
        exit(1)

    print("Iniciando broker Mosquitto con TLS...")
    proc = subprocess.Popen(
        ["mosquitto", "-c", conf_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        if _broker_running():
            print("Broker Mosquitto listo en localhost:8883 (TLS)")
            return proc
        time.sleep(0.1)
    raise RuntimeError("Mosquitto no levantó a tiempo.")

def stop_broker(proc):
    if proc and proc.poll() is None:
        print("Deteniendo broker Mosquitto...")
        proc.terminate()
        proc.wait()

class SensorVirtual:
    def __init__(self, id, tipo):
        self.id = id
        self.tipo = tipo
    
    def leer_valor(self):
        # Simular fallo de lectura del sensor (10% probabilidad)
        if random.random() < 0.1:
            raise Exception("Error de hardware en sensor")
            
        if self.tipo == "temperatura":
            return round(random.uniform(18, 30), 2)
        return random.randint(0, 100)

# ── Main ──────────────────────────────────────────────────────────────────────

broker_proc = start_broker()

# ── Clientes MQTT con TLS ─────────────────────────────────────────────────────

connected_local = False
connected_remote = False

def on_connect_local(client, userdata, flags, reason_code, properties):
    global connected_local
    if reason_code == 0 or str(reason_code) == "Success":
        connected_local = True
        print(f"✓ Conectado a broker LOCAL {BROKER_LOCAL}:{PORT}")
    else:
        print(f"Error conectando a broker LOCAL: {reason_code}")

def on_connect_remote(client, userdata, flags, reason_code, properties):
    global connected_remote
    if reason_code == 0 or str(reason_code) == "Success":
        connected_remote = True
        print(f"✓ Conectado a broker REMOTO {BROKER_REMOTE}:{PORT}")
    else:
        print(f"Error conectando a broker REMOTO: {reason_code}")

# Cliente local con certificado local
client_local = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sensor-er-local-{os.getpid()}")
client_local.tls_set(ca_certs=CA_CERT_LOCAL)
client_local.on_connect = on_connect_local

# Cliente remoto con certificados del sistema
client_remote = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sensor-er-remote-{os.getpid()}")
client_remote.tls_set()  # Usa certificados del sistema
client_remote.on_connect = on_connect_remote

# Conectar a broker local
try:
    client_local.connect(BROKER_LOCAL, PORT, 60)
    client_local.loop_start()
except Exception as e:
    print(f"⚠ No se pudo conectar a broker local: {e}")
    client_local = None

# Conectar a broker remoto
try:
    client_remote.connect(BROKER_REMOTE, PORT, 60)
    client_remote.loop_start()
except Exception as e:
    print(f"⚠ No se pudo conectar a broker remoto: {e}")
    client_remote = None

# Esperar conexiones (máx 10s)
for _ in range(100):
    if (not client_local or connected_local) and (not client_remote or connected_remote):
        break
    time.sleep(0.1)

if not connected_local and not connected_remote:
    print("ERROR: No se pudo conectar a ningún broker")
    stop_broker(broker_proc)
    exit(1)

async def enviar_con_reintento(data):
    """
    Intenta enviar datos por MQTT con reintentos y simulación de errores.
    """
    for i in range(3):
        try:
            # Simular error aleatorio de RED (40% de probabilidad)
            if random.random() < 0.4:
                print(f"--- [SIMULACION] Generando error de red (Intento {i+1}) ---")
                raise Exception("Error de red simulado")

            payload = json.dumps(data)
            
            # Publicar en broker local
            if client_local and connected_local:
                info = client_local.publish(TOPIC, payload)
                info.wait_for_publish()
                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[LOCAL] Publicado exitosamente: {payload}")
            
            # Publicar en broker remoto
            if client_remote and connected_remote:
                info = client_remote.publish(TOPIC, payload)
                info.wait_for_publish()
                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[REMOTO] Publicado exitosamente: {payload}")
            
            return True
            
        except Exception as e:
            print(f"Fallo intento {i+1} ({e}). Reintentando en 2s...")
            await asyncio.sleep(2)
    
    print("Error: Se agotaron los reintentos.")
    return False

async def main():
    sensor = SensorVirtual("SENSOR_ER_01", "temperatura")
    print(f"Iniciando sensor {sensor.id}...")
    
    while True:
        try:
            valor = sensor.leer_valor()
            timestamp = datetime.now().isoformat()
            datos = {
                "sensor_id": sensor.id, 
                "valor": valor,
                "timestamp": timestamp
            }
            
            print(f"[{timestamp}] Generando dato: {valor}")
            await enviar_con_reintento(datos)
        except Exception as e:
            print(f"Error leyendo sensor: {e}")
        
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDeteniendo sensor...")
        if client_local:
            client_local.loop_stop()
            client_local.disconnect()
        if client_remote:
            client_remote.loop_stop()
            client_remote.disconnect()
        stop_broker(broker_proc)
