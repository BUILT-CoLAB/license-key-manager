from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCk8QtER0SUC0ORKHqo31rRAlqv
854rXRBwYR5atwSjPHVxCFFASdHngsVRCCUkEfKiW8FlRO71NdYMO8yrTC/+pkMp
SbR2vQDIDqrFfQ7mXmjJeL7Jl8sNxJ82HMvuz71hXyrodjkSjd3AmdXUJ6FYNXB0
bPNFEwBMvmUUmDU5sQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '3a228d02-f489-4a5d-acc6-872af0b75b7a'
serial = 'TTICG-PGTW3-NFQPD-0OPSH'
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


