import asyncio
import json
import random
import subprocess
import socket
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# ── Configuración ─────────────────────────────────────────────────────────────

BROKER = "localhost"
PORT   = 1883
TOPIC  = "fadena/test"

# ── Mosquitto local ───────────────────────────────────────────────────────────

def _broker_running() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((BROKER, PORT)) == 0

def start_broker():
    if _broker_running():
        print("Broker Mosquitto ya está corriendo.")
        return None

    mosquitto_path = subprocess.run(
        ["which", "mosquitto"], capture_output=True, text=True
    ).stdout.strip()

    if not mosquitto_path:
        print("ERROR: Mosquitto no está instalado. Instalalo con: sudo apt install mosquitto")
        exit(1)

    print("Iniciando broker Mosquitto local...")
    proc = subprocess.Popen(
        ["mosquitto", "-p", str(PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(50):
        if _broker_running():
            print(f"Broker Mosquitto listo en {BROKER}:{PORT}")
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

# Configuración MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "fadena/test"

# ── Main ──────────────────────────────────────────────────────────────────────

broker_proc = start_broker()

# Inicializar cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Error fatal conectando al broker: {e}")
    exit(1)

async def enviar_con_reintento(data):
    """
    Intenta enviar datos por MQTT con reintentos y simulación de errores.
    """
    for i in range(3): # 3 intentos
        try:
            # Simular error aleatorio de RED (40% de probabilidad)
            if random.random() < 0.4:
                print(f"--- [SIMULACION] Generando error de red (Intento {i+1}) ---")
                raise Exception("Error de red simulado")

            payload = json.dumps(data)
            
            info = client.publish(TOPIC, payload)
            info.wait_for_publish() 
            
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise Exception(f"Error MQTT RC: {info.rc}")

            print(f"Publicado exitosamente: {payload}")
            return True # Éxito
            
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
            # Añadir timestamp ISO 8601
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
        
        # Esperar antes de la siguiente lectura
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDeteniendo sensor...")
        client.loop_stop()
        client.disconnect()
        stop_broker(broker_proc)
