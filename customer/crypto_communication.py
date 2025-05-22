import json
import os
import traceback
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    if not os.path.exists("/keys"):
        os.makedirs("/keys")
    if not os.path.exists("/keys/shared"):
        os.makedirs("/keys/shared")

    with open("/keys/ecc_key_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open("/keys/shared/ecc_key_public.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return private_key, public_key

def encrypt_message(message):
    try:
        with open("/keys/bank/ecc_key_public.pem", "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read()
            )

        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            return None, None, None

        ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
        ephemeral_public_key = ephemeral_private_key.public_key()

        shared_key = ephemeral_private_key.exchange(ec.ECDH(), public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'ecies-demo',
        ).derive(shared_key)

        iv = os.urandom(16)

        encryptor = Cipher(algorithms.AES(derived_key), modes.GCM(iv)).encryptor()
        ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()


        serialized_ephemeral_key = ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return {
            'ephemeral_key': serialized_ephemeral_key.hex(),
            'iv': iv.hex(),
            'ciphertext': ciphertext.hex(),
            'tag': encryptor.tag.hex()
        }
    except:
        print(traceback.format_exc())
        return ''

def decrypt_message(encrypted_package):
    try:
        with open("/keys/ecc_key_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )

        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            return None, None, None

        ephemeral_public_key = serialization.load_pem_public_key(encrypted_package['ephemeral_key'])

        if not isinstance(ephemeral_public_key, ec.EllipticCurvePublicKey):
            return None, None, None

        shared_key = private_key.exchange(ec.ECDH(), ephemeral_public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'ecies-demo',
        ).derive(shared_key)

        iv = encrypted_package['iv']
        decryptor = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv, encrypted_package['tag'])
        ).decryptor()

        plaintext = decryptor.update(encrypted_package['ciphertext']) + decryptor.finalize()
        return plaintext.decode('utf-8')
    except:
        print(traceback.format_exc())
        return ''
