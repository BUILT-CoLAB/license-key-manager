from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2xLOGfCjj4hYyStE+dQudzbaM
mOVPqpXYuPLasgk9mYa/kyx6ElRn3qmkeQ7awxdUT2A3SUB3NpsVF2ODXKUiK1fx
7iUsyG1817K/M2OeLYThDDuEzotirNLJluelvo7eTQk3u5hc2QXScZ0nP9L8aTlu
Q2P5Pum1o2KDgfy9ewIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = 'b4df7b73-129f-4771-b527-19a321e3e7fd'
serial = 'W28DL-6BUN6-88QB7-C4PB8'
hwid= 'TestingHWID_2' # Deterministic UID

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


