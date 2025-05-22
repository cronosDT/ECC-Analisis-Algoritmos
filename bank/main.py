import traceback
from typing import Union
import uvicorn
from fastapi import FastAPI
import time
from ecc import generate_keys_ecdsa, sign_ecdsa, verify_signature_ecdsa
from crypto_communication import generate_ecc_key_pair, decrypt_message, encrypt_message
import json
from db_sqlite import init_db

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
    sign_ecdsa(data.nombre, dynamic_key.encode('utf-8'))
    return {"key": encrypt_message(dynamic_key)}

@app.post("/validate")
def validate(item: VerifyKey):
    try:
        verification = False
        encrypted_data = json.loads(item.key)
        encrypted_bytes = {
            'ephemeral_key': bytes.fromhex(encrypted_data['ephemeral_key']),
            'iv': bytes.fromhex(encrypted_data['iv']),
            'ciphertext': bytes.fromhex(encrypted_data['ciphertext']),
            'tag': bytes.fromhex(encrypted_data['tag'])
        }
        decrypted_key = decrypt_message(encrypted_bytes)
        if isinstance(decrypted_key, str):
            verification = verify_signature_ecdsa(item.nombre, decrypted_key.encode('utf-8'))
        return {"verification": 'Clave válida' if verification else 'Clave no válida'}
    except Exception as e:
        print(traceback.format_exc())
        return {"verification": f'Error en validación: {str(e)}'}

if __name__ == "__main__":
    init_db()
    generate_keys_ecdsa()
    generate_ecc_key_pair()
    uvicorn.run(app, host="0.0.0.0", port=8080)