from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives  import serialization
from .models import Product

def create_product(new_name,new_logo):
    private_key = Ed25519PrivateKey.generate()
    api_key = uuid4()
    
    public_key = private_key.public_key()
    newProduct = Product(name=new_name,logo=new_logo,privateK=private_key.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()),publicK=public_key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw),apiK=str(api_key))
    
    return newProduct

def generate_license_key(product_id,user_email):
    return "lel"

