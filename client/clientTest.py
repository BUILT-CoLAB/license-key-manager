from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC07vQZz1vK2s9fyi8YTqu/RUYd
wkzlNrWXLdNx3aQpAzzprwoMe/f0bMm7o1pO6MM3apPmGmCL+EcKt7dqzF3iTFO9
9kRV5Rsw9dFqfYcljLjZ3BuBM0UGO+kZxN1hFvxNpdcyzypbNKXVbLtwtcMYfAg2
ELSRzXOS7hl8Xyg3xwIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = 'f751fa4a-d4df-4519-815d-92cc3019709b'
serial = 'XBHTI-I9QGF-AV2LY-IPYUL'
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


