import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

app = FastAPI(title="IoT Sensor WebSocket Server")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"Client connected: {websocket.client}")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                temp = message.get("temperature")
                timestamp = message.get("timestamp")
                print(f"[{timestamp}] Received temperature: {temp}°C")
                
                # Echo back confirmation
                await websocket.send_text(f"Received data: {temp} at {timestamp}")
            except json.JSONDecodeError:
                print(f"Received non-JSON data: {data}")
                await websocket.send_text(f"Error: Invalid JSON")
    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
