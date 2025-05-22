import traceback
from typing import Union
import uvicorn
from fastapi import FastAPI
import time
import json

app = FastAPI()

from pydantic import BaseModel

class GenerateTicketRequest(BaseModel):
    nombre: str

class VerifyKey(BaseModel):
    nombre: str
    key: str

@app.post("/key")
def get_key(data: GenerateTicketRequest):
    dynamic_key = str(int(time.time()) % 10**6).zfill(6)
    return {"key": dynamic_key}

@app.post("/validate")
def validate(item: VerifyKey):
        return {"verification": 'Clave válida' if True else 'Clave no válida'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
