import base64
import requests
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


def authentication(public_key, api_key, serial, hwid):
    """
    Connects to the server and authenticates the license
    """
    plaintexts = bytes(serial + ':' + hwid, 'utf-8')

    if isinstance(public_key, rsa.RSAPublicKey):

        payload = public_key.encrypt(
            plaintexts,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # "9XAG0-OMRZ8-ZYZPT-5AHYO:CPU0_BFEBFBFF000806C1_ToBeFilledByO.E.M."
        #print(plaintexts)
        final_payload = base64.b64encode(payload).decode('utf-8')
        #print(final_payload)
        request_path = 'https://slm.v2202209180882200160.nicesrv.de/api/v1/validate'
        server_request = requests.post(request_path, json={
            "apiKey": api_key, "payload": final_payload
        }, timeout=10)

        response_code = server_request.json()['Code']
        success_codes=['OKAY', 'SUCCESS']

        if any(response_code in i for i in success_codes):
            print(f"Authentication: {response_code}")
            return True

        print(f"Error: {response_code}")
        return False

if __name__ == "__main__":

    PUB_KEY = """-----BEGIN PUBLIC KEY----- 
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApLdNmLay94jt4bgJBtpu 
OiGLRwJC7rWwAA4NpR/vjFMbRLT+52ugnqhv0Oej1T5D3Za7hRfrMQzSeXzmuhMP 
V2fEPdqgizFjydTgrvxgluaWByCfDEMEEBpihihhZnkCx9YYoz3ig8C+I9nVZ3C7 
ntfRaOqTslNVfDSqAR+6DulpmISkMxkFvHkJt09NlP2iqPlzSKC5mtFJjbLKt4cW 
pMESNVBTFrnhqxvhxwgQ2KbH54XdBpzKhX2aYzQBNEG9toOJxBSqbG2iXKZ09n7s 
uEVELXqVF+1+cEv2zaE6HFxBYuHOjcAXUXG/xLs+JKWuosozAQmUUpvx7pBPcHOr 
nwIDAQAB 
-----END PUBLIC KEY-----
"""

    PUBLIC_KEY = serialization.load_pem_public_key(str.encode(PUB_KEY))
    API_KEY = '823c2011-cd0c-41db-a7c9-0906ec42e7aa'
    SERIAL = 'A2UV9-9HZYZ-UWFK8-SS71A'
    HWID = 'CPU0_BFEBFBFF000806C3_ToBeFilledByO.E.M.'  # Deterministic UID

    authentication(PUBLIC_KEY, API_KEY, SERIAL, HWID)
    