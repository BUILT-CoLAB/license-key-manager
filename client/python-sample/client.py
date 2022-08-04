from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6rS3LTgnh9quJ+AdiHjM
SHG2KXh6Li5cPId1XSElia1WOS4j0jNLScSGVS28naD6254YCZqkN8zdGt62RlAY
dAErrcaYR5dbhIJ91uiKI/7yucr8TA8l2Pao7XRCqWNeqhsakoiATHye9Xvqsoo6
sN8EaVACrIl7Cd0w1UlWowVw9cxXZO5qj2ebUhpJqS7+g4c2cx1fhmI9Kl4dZvid
iJCIMJNxHMZL80ZcxftalR8xuuNnnvScbv84twhmh2NXeelK7rddVj9ZJfs2MIWt
ReGxJyjrd9pdkn0xUCIlqlTswB/+BLR8kznAbXkvSyNnyS9PHt9LyAGzRiJXuiaL
qwIDAQAB
-----END PUBLIC KEY-----"""

public_key = serialization.load_pem_public_key(str.encode(publicKey))

api_key = '3ebec076-b65f-4e5d-bc3a-27846b13bffb'
serial = '9XAG0-OMRZ8-ZYZPT-5AHYO'
hwid = 'CPU0_BFEBFBFF000806C1_ToBeFilledByO.E.M.'  # Deterministic UID

plaintexts = bytes(serial + ':' + hwid, 'utf-8')


if(isinstance(public_key, rsa.RSAPublicKey)):

    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # "9XAG0-OMRZ8-ZYZPT-5AHYO:CPU0_BFEBFBFF000806C1_ToBeFilledByO.E.M."
    print(plaintexts)
    final_payload = base64.b64encode(payload).decode('utf-8')
    print(final_payload)
    r = requests.post('http://127.0.0.1:5000/api/v1/validate', json={
        "apiKey": api_key, "payload": final_payload
    })

    print(f"Response: {r.json()}")
