from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDiPW3I+9vzMs6OcrMgVzqmR34z
SYGSK5UXl01863jX0rkcoLm3W9PIQsHFQUVc9A9FzfSm9dU9voyp4DBvOzx1xS7z
qDiANulv33DUa49d3eO7682psyRcXikUT0X3ha1LZs366fNhJibtcIqO8EcY9AzF
5hCMbJoIISF2JLsjRwIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '7411bbe2-d524-4dd5-a98e-80e96e057432'
serial = '9V4VI-SNTI3-9NDS5-P5JZZ'
hwid= 'TestingHWID_N1' # Deterministic UID

plaintexts = bytes(serial + ':' + hwid[:23],'utf-8')

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
    final_payload=base64.b64encode(payload).decode('utf-8')
    
    r = requests.post('http://127.0.0.1:8150/validate',json={
        "apiKey":api_key,"payload":final_payload
    })

    print(f"Response: {r.json()}")


