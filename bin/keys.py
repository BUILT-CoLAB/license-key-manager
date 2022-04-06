from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from flask import Blueprint, request
from . import db


keys = Blueprint('keys',__name__,url_prefix='/lkey')

@keys.route('/create',methods=['POST'])
def create():
    private_key = Ed25519PrivateKey.generate()
    signature = private_key.sign(b"my authenticated message")
    public_key = private_key.public_key()
    # Raises InvalidSignature if verification fails
    public_key.verify(signature, b"my authenticated message")

    return {
        'message': 'working',
        'method': 'POST'
    }
