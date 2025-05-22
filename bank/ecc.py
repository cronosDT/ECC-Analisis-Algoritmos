from ecdsa import SigningKey, NIST256p, VerifyingKey
import hashlib
import os
from db_sqlite import save_signature_to_db, get_latest_signature_by_name, is_signature_expired

def generate_keys_ecdsa():
    private_key = SigningKey.generate(curve=NIST256p)
    public_key = private_key.verifying_key

    if not os.path.exists("/keys"):
        os.makedirs("/keys")
    if not os.path.exists("/keys/shared"):
        os.makedirs("/keys/shared")

    with open("/keys/ecdsa_key_private.pem", "wb") as f:
        f.write(private_key.to_pem())

    with open("/keys/shared/ecdsa_key_public.pem", "wb") as f:
        if public_key:
            f.write(public_key.to_pem())

def sign_ecdsa(nombre: str, password: bytes):
    with open("/keys/ecdsa_key_private.pem", "rb") as f:
        private_key = SigningKey.from_pem(f.read())

    signature = private_key.sign(password, hashfunc=hashlib.sha256)
    save_signature_to_db(nombre, signature)
    return True

def verify_signature_ecdsa(nombre: str, password: bytes):
    try:
        with open("/keys/shared/ecdsa_key_public.pem", "rb") as f:
            public_key = VerifyingKey.from_pem(f.read())

        record = get_latest_signature_by_name(nombre)
        if not record:
            return False

        signature = record["signature"]
        timestamp = record["timestamp"]

        if is_signature_expired(timestamp):
            print("Firma expirada.")
            return False

        return public_key.verify(signature, password, hashfunc=hashlib.sha256)
    except Exception as e:
        print(f"Error de verificación ECDSA: {e}")
        return False