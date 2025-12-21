import asyncio
import json
import random
from datetime import datetime
import paho.mqtt.client as mqtt

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
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/telemetria"

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
