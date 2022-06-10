from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+JQnSskYXyuuP7+hDWLxzn7EJ
lbaOlVu4jT+2r4YLTmeWvKhM6xNIxeSYx4J5DaUBiS1Nj4Aa1N7DEf6JlQSINxWE
JhBr8PyE3TkrvVrjnL6JC0slPZGIMoTQiRWyEzJUenejXGXA5ewwagha+1wU58kq
XKeEuPgR63ZLvgIzAQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '51131a2f-fd57-4c86-b41a-c26f21fe108b'
serial = 'X7HYM-BIKBA-J4HIK-HPGME'
hwid= 'TestingHWID_N5' # Deterministic UID

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


