import asyncio
from aiocoap import *
import json
import random
from datetime import datetime

async def simulate_sensor():
    context = await Context.create_client_context()
    uri = "coap://localhost/temp"
    
    print(f"CoAP Client started, sending to {uri}")
    
    try:
        while True:
            # Simulate temperature reading
            temp = round(random.uniform(20.0, 30.0), 2)
            timestamp = datetime.now().isoformat()
            
            payload_dict = {
                "temperature": temp,
                "timestamp": timestamp
            }
            
            payload = json.dumps(payload_dict).encode('utf-8')
            
            # Create POST request
            request = Message(code=POST, payload=payload, uri=uri)
            
            print(f"Sending CoAP POST: {payload_dict}")
            try:
                response = await context.request(request).response
                print(f"Server response: {response.code} - {response.payload.decode('utf-8')}")
            except Exception as e:
                print(f"Failed to send CoAP request: {e}")
            
            # Wait before next reading
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        print("\nSimulation stopped")

if __name__ == "__main__":
    asyncio.run(simulate_sensor())
