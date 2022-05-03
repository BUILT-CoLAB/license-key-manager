from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDtk6/DwflYICLE+JKBLc6HTOHd
12qSFxApeea2dHsrg6JZ8nLqeRI/CX8SfPiuJOXHVdR46uC1UMgGVTbq27uPGgsl
XlLXbNppx18b+jD5PUUgVd6BWa5+ZmpWYleQdHmiysG2Hgg0htqtwNEiyhXNajUT
oOesGyB1QASRNig/gwIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '072c95b0-bacb-4b53-9102-600651825cfa'
serial = '0RBXU-GQYO5-37J7B-S1E8W'
hwid= 'TestingHWID_N4' # Deterministic UID

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


