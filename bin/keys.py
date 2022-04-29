from uuid import uuid4,uuid1
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

def create_product_keys():
    private_key = rsa.generate_private_key(size=1024,public_exponent=65537)
    api_key = uuid4()
    
    public_key = private_key.public_key()
    
    
    return [private_key,public_key,api_key]

def get_private_key(product):
    return serialization.load_ssh_private_key(product.privateK,password=None)

def generate_new_serial_key():
    return uuid1()


# Formato dos dados: licensekey-hardwareID 
def decrypt_data(payload,product):
    private_key = get_private_key(product)
    
    plaintext = private_key.decrypt(
        payload,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
    ))
    print(plaintext)
    return plaintext


    
