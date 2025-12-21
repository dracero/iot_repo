import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Lectura(BaseModel):
    sensor_id: str
    valor: float

@app.post("/telemetria")
async def recibir_data(data: Lectura):
    print(f"Recibido: {data}")
    return {"status": "recibido", "sensor": data.sensor_id, "valor": data.valor}

if __name__ == "__main__":
    print("Iniciando servidor de lectura en http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)