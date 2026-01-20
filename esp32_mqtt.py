import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# Configuration
WIFI_SSID = "Wokwi-GUEST" # Replace with your open wifi SSID if different
MQTT_BROKER = "mqtt-dashboard.com"
CLIENT_ID = "fadena_id"
TOPIC_SUB = "esp32-sub"
TOPIC_PUB = "fadena/test"
DHT_PIN = 8

def connect_wifi():
    print("Connecting to Wi-Fi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, "")
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.1)
    print(" Connected!")
    print("Network config:", sta_if.ifconfig())

def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'esp32-sub' and msg == b'reset':
        print('Resetting...')
        machine.reset()

def connect_mqtt():
    print("Connecting to MQTT Broker...", end="")
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(TOPIC_SUB)
    print(" Connected!")
    return client

def main():
    connect_wifi()
    client = connect_mqtt()
    
    sensor = dht.DHT22(Pin(DHT_PIN))

    while True:
        try:
            client.check_msg()
            
            # Read sensor
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            
            msg = ujson.dumps({
                "temp": temp,
                "humidity": hum,
                "client_id": CLIENT_ID
            })
            
            print(f"Publishing: {msg} to {TOPIC_PUB}")
            client.publish(TOPIC_PUB, msg)
            
            time.sleep(5)
            
        except OSError as e:
            print("Failed to read sensor or publish:", e)
            try:
                client.connect() # Reconnect if lost
            except:
                pass 
            time.sleep(5)

if __name__ == "__main__":
    main()
