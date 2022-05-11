from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCxtr0kGDL1jFuCYuu9lS/hIlvL
OfSNJtLY7v3xygEqnexMoY1pLHqx+uOysW5x/tMCx3UrJG+/pP7zZC6gcuHmfNCD
DBLCsvmTrn9ONenJNBNLg20fXntKGfkWw8d2yS5mC9SGY0HhR+hMoilfLcZ1FCZR
T6tE85KkLxHjLMLuYQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '7a98c7e2-a62d-4dd7-930c-b14c34d08e50'
serial = '97ILY-DPIWQ-LUIFQ-IDZL5'
hwid= 'TestingHWID_N3' # Deterministic UID

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
    
    r = requests.post('http://127.0.0.1:5000/validate',json={
        "apiKey":api_key,"payload":final_payload
    })

    print(f"Response: {r.json()}")


