import asyncio
import websockets
import json
import random
from datetime import datetime

async def simulate_sensor():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        try:
            while True:
                # Simulate temperature reading
                temp = round(random.uniform(20.0, 30.0), 2)
                timestamp = datetime.now().isoformat()
                
                payload = {
                    "temperature": temp,
                    "timestamp": timestamp
                }
                
                # Send data
                print(f"Sending: {payload}")
                await websocket.send(json.dumps(payload))
                
                # Wait for server response
                response = await websocket.recv()
                print(f"Server response: {response}")
                
                # Wait before next reading
                await asyncio.sleep(2)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")

if __name__ == "__main__":
    try:
        asyncio.run(simulate_sensor())
    except KeyboardInterrupt:
        print("\nSimulation stopped")
