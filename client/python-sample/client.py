from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqmZjmBKJo7p1Luadbpuj
CziIXxY4FpkXQm5lL+jJ/xLzE5qBT2wqAZqJNSotIZPej3NZkVmwHB0aTSfkNSQG
F2h93oxtTRFy6NVJVfQ9BSD8pS5/aH3eTbQr97ki/WJL4b6x5gaZ48pYAsHBps/I
Mj5cMXuIVtMeRaP+ghIL3mD3ecUoCdTtyQF3P7LOP4gUA2gLPafbXeMZbM73ErzL
7KikChul1F0nqnm5ZOffb9FHXHaLPZmoBcU5jRkCqxnxWzQXOAknTSxRou9s6qMF
0ZR9BrKIwGBIjzLIzOYXySeGRuHa60Pjg8Ip2/RDk6MbuUGOwtseGTeGr3Izu1uc
SQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key(str.encode(publicKey))

api_key = '9d9aad2b-8aed-4943-8f03-0910ae5a6336'
serial = 'ANQMD-IMHRR-8MGZG-U7TLL'
hwid = 'CPU0_BFEBFBFF000806C3_ToBeFilledByO.E.M.'  # Deterministic UID

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
    r = requests.post('http://localhost:8000/api/v1/validate', json={
        "apiKey": api_key, "payload": final_payload
    }, timeout=10)

    print(f"Response: {r.json()}")
