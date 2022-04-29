from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

with open('../public_key_file',"rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read()
    )

api_key = 'd73f7698-9ad8-4240-acda-d7a93b5f1f29'
serial = 'b8ccc8c0-c7a9-11ec-853d-3c9509696017'
hwid= 'db4fd6b2-c7a9-11ec-9c53'#gerar uuid deterministico

plaintexts = bytes(serial+':'+hwid[:23],'utf-8')

if(isinstance(public_key,rsa.RSAPublicKey)):

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


