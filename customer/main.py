from typing import Union
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import json
from crypto_communication import generate_ecc_key_pair, encrypt_message, decrypt_message

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BANK_URL = "http://bank:8080"

class VerifyKey(BaseModel):
    nombre: str
    key: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get-key", response_class=HTMLResponse)
async def get_key_form(request: Request):
    return templates.TemplateResponse("get_key.html", {"request": request})

@app.post("/get-key", response_class=HTMLResponse)
async def get_key_submit(request: Request, nombre: str = Form(...)):
    response = requests.post(f"{BANK_URL}/key", json={"nombre": nombre})
    data = response.json()
    encrypted_data = data['key']
    encrypted_bytes = {
        'ephemeral_key': bytes.fromhex(encrypted_data['ephemeral_key']),
        'iv': bytes.fromhex(encrypted_data['iv']),
        'ciphertext': bytes.fromhex(encrypted_data['ciphertext']),
        'tag': bytes.fromhex(encrypted_data['tag'])
    }
    decrypted_key = decrypt_message(encrypted_bytes)
    return templates.TemplateResponse("key.html", {
        "request": request,
        "original_key": encrypted_data,
        "decrypted_key": decrypted_key,
        "nombre": nombre
    })

@app.post("/validate-key", response_class=HTMLResponse)
async def validate_key(request: Request, nombre: str = Form(...), key: str = Form(...)):
    encrypted_package = encrypt_message(key)
    response = requests.post(
        f"{BANK_URL}/validate",
        json={"nombre": nombre, "key": json.dumps(encrypted_package)}
    )
    result = response.json()
    return templates.TemplateResponse("validation.html", {
        "request": request,
        "validation_result": result['verification'],
        "key_attempt": key,
        "nombre": nombre
    })

if __name__ == "__main__":
    generate_ecc_key_pair()
    uvicorn.run(app, host="0.0.0.0", port=8090)
