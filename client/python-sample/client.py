from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3iTYnI6MQhcX4YUa1cP7
5ACmKKV2aRckk/tBkXd8qXNzofE9zvlaAaOlR4vubGRRIZz4gtFEvJan/Dy/TekT
Nph6wzjeBszRZDZSLknhyJMmMQxxEgKbWjwLNUfHjFfpY6wlmnZwcERBpxUIaNlI
889IJF8zDik9Wg5R3j1DEPoLWDL8flMJUpWN9A4FQXPvUUXgluUmFHU4GpCwgHEF
NywpcwMEVlGbVTJyVf12y0p8R4xWEg8fREzA7RoBuSa51apzAzFoGyT6gD4NT7nE
FVX1LFjk3G/JivIhqZq4DevuPX92vMCKvgvoocaSdpgqavgQ+KA+m7a5bR2TIFKq
rQIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key(str.encode(publicKey))

api_key = '474a7bca-92fd-46cc-b754-5ca783cf37e8'
serial = 'YESKG-FQ6TJ-XIE8R-CRW99'
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
    })

    print(f"Response: {r.json()}")
