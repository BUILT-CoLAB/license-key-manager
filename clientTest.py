from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from uuid import uuid1
import requests
import base64

publicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIn0QY3MOuU88QhD+qj5+iCznA
kWT3IKlWWHgMcGSi4Vzhh6WD1fFgd4pvf01dox8w2SQVTbRGWTC2W96e/kOu9L9X
Htfz0DE1LHnSRIGH9uKXzauZ3pLnfP0fT8aZtJeYfQCAsCDzsybwI/jr4oPLGE+j
yBxSAd0lUsss5deZswIDAQAB
-----END PUBLIC KEY-----
"""

public_key = serialization.load_pem_public_key( str.encode(publicKey) )

api_key = '3aee11c2-c977-4e30-91e8-a0d9853cecd0'
serial = 'HB474-V8UAW-ZE8IQ-36E9V'
hwid= 'GPPPPAA112381299' # Deterministic UID

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


