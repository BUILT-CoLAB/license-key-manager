from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC2F2bV0KErkLrzcox/uaBR5hXy
1VJ8urKUfOoLybOelAt2nPfsnz1OKJO5RGrysUgQUwpBhjmTa2wDngB0/5sGFCRT
MLha5yVdEPN1umJKBdzxO/L/bYitK3SkucmiYiHI/t4JkJLu+4x8/SShARchqzw/
ttmbB6O8tw8sigqGawIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key(str.encode(publicKey))

api_key = 'f8e6f453-bd47-4576-a0de-3a06a35a453d'
serial = 'QT074-6MWAP-5DNQ7-440DZ'
hwid = 'TestingHWID_N2'  # Deterministic UID

plaintexts = bytes(serial + ':' + hwid[:23], 'utf-8')

if(isinstance(public_key, rsa.RSAPublicKey)):

    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print(plaintexts)
    final_payload = base64.b64encode(payload).decode('utf-8')

    r = requests.post('http://127.0.0.1:5000/validate', json={
        "apiKey": api_key, "payload": final_payload
    })

    print(f"Response: {r.json()}")
