from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDi5kP3dMdzwaHRoEPmlKXAz+rI
GuvdVCtAP+EFYeZ6HpFBT4S/O4bR4F5+xUmi//86TmyLeD2lkxa1TmqnPSm535qf
FMi746XwKrIdMbdNtWBGokDJgkDZmg/K+bGOrZZDP1V7o+op0yfFFUSkTc+ATYG+
W1UF/W0CNfcDwwqpwQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '621e2ff0-75b9-47d3-b164-c5474b08b247'
serial = 'OFIP3-C439E-Q4OIB-CCJ1Q'
hwid= 'TestingHWID_N2' # Deterministic UID

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


