from uuid import uuid4,uuid1
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from .models import Product

def create_product(new_name,new_logo):
    private_key = rsa.generate_private_key(size=1024,public_exponent=65537)
    api_key = uuid4()
    
    public_key = private_key.public_key()
    newProduct = Product(name=new_name,logo=new_logo,privateK=private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption()),publicK=public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo),apiK=str(api_key))
    
    return newProduct

def get_private_key(product):
    return serialization.load_ssh_private_key(product.privateK,password=None)

def generate_new_serial_key(hardwareID):
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


    
