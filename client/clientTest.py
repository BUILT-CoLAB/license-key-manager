from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDVpELyef7dYfnC1cismXIUVI9A
ZDWaxlmZWh41hx8e9ECsWFj29qnjDEw/z67AvFso5V3a679Sh6D5puebnbo5ledJ
/TE7MT2di8s42RcRTWMkUJcS6/OBk5PoQLEkoZytS5Dguh45mRFccLp6SkpvVNT9
G8cLTLKt7jSBwTnpiQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '5ef8f2e0-c659-416c-8e57-adeed9361028'
serial = 'VKJO6-GBDR7-CV5IG-F5Y7U'
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
    
    r = requests.post('http://127.0.0.1:5000/validate',json={
        "apiKey":api_key,"payload":final_payload
    })

    print(f"Response: {r.json()}")


