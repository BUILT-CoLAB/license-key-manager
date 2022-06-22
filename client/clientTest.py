from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDk8AytZwwmVaBfIpdQsOsCnrhp
HLe3ecYuwsu+xSLJINaSoP68hNLmYpFd4k5f4eLMu81CPcZZwHOc5xkweoN5mHbj
D2CXCb2CYbKvpSSLNObfkUwCotPmdEXrY7jW7N1cHucTql/myTbS/cTGzjHZa/sz
2xnA6wJ7f+Qi9VJNVQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '6b67afa9-358f-44fe-8d92-c86a2e6c1e89'
serial = 'Q2ERJ-V8DBY-AEWAI-VH1TJ'
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


