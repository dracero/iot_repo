import asyncio
import aiocoap.resource as resource
import aiocoap
import json

class TemperatureResource(resource.Resource):
    """Resource that handles temperature readings via POST requests."""

    async def render_post(self, request):
        try:
            payload = json.loads(request.payload.decode('utf-8'))
            temp = payload.get("temperature")
            timestamp = payload.get("timestamp")
            print(f"[{timestamp}] CoAP Received temperature: {temp}°C")
            
            response_payload = json.dumps({"status": "received", "temp": temp}).encode('utf-8')
            return aiocoap.Message(payload=response_payload, code=aiocoap.CHANGED)
        except Exception as e:
            print(f"Error processing CoAP request: {e}")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

async def main():
    # Resource tree registration
    root = resource.Site()
    root.add_resource(['temp'], TemperatureResource())

    print("Starting CoAP server on localhost:5683...")
    await aiocoap.Context.create_server_context(root, bind=('localhost', 5683))

    # Run forever
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCoAP Server stopped")
