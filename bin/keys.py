from uuid import uuid4,uuid1
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import base64

def create_product_keys():
    private_key = rsa.generate_private_key(key_size=1024,public_exponent=65537)
    api_key = uuid4()
    
    public_key = private_key.public_key().public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo)

    with open('public_key_file','wb') as public_key_out:
        public_key_out.write(public_key)
    
    return [private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption())
            ,public_key,
            str(api_key)]

def get_private_key(product):
    return serialization.load_pem_private_key(product.privateK,password=None)

def generate_new_serial_key():
    return str(uuid1())


# Formato dos dados: licensekey-hardwareID 
def decrypt_data(payload,product):
    private_key = get_private_key(product)
    
    original_payload= base64.b64decode(payload.encode('utf-8'))
    
    plaintext = private_key.decrypt(
        original_payload,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
    ))
    print(plaintext)
    return plaintext.decode('utf-8').split(':')


    
