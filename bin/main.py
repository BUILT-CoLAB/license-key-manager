from asyncio.windows_events import NULL
from lib2to3.pgen2 import token
from flask import Blueprint, render_template, request
from flask_httpauth import HTTPTokenAuth
from regex import P
from sqlalchemy import text, true,select
from .models import Product
import random
import string
import json
from . import db
from . import _KEY_LENGTH_
from .keys import create_product, decrypt_data, verify_data

main = Blueprint('main', __name__)

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    tokens = Product.query.filter_by(apiK=token).first()
    if tokens is None:
        return None

    return tokens

#
# sql = text('SELECT * FROM product')
# result = db.engine.execute(sql)
#

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

###########################################################################

@main.route('/cpanel')
def cpanel():
    getProduct("hey")
    return render_template('cpanel.html')

@main.route('/cpanel/product/create', methods=['POST'])
def createProduct():
    dataInfo = request.get_json()
    print(dataInfo)

    # ################# Storage Data ####################    
    name = dataInfo.get('name')
    logo = dataInfo.get('URL')
    # ###################################################
    new_product = create_product(name,logo)
    db.session.add(new_product)
    db.session.commit()
    return "OKAY"

###########################################################################

@main.route('/cpanel/product/id/<productid>')
def productDisplay(productid):
    return render_template('product.html', prodID = productid)

@main.route('/cpanel/product/id/<productid>/createkey')
def createKey(productid):
    return render_template('product.html', prodID = productid)

def getProduct(searchString):
    products = Product.query.all()
    for product in products:
        print(product.name)
        print(product.logo)
        print(product.privateK)
        print(product.publicK)
        print(product.apiK)

def generateAPIKey(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    apiKey = ''.join(random.choice(characters) for i in range(length))
    return apiKey


@main.route('/validate',methods=['POST'])
def validate_product():
    dataInfo = request.get_json()
    
    # Validating user with api key
    product = verify_token(dataInfo['apiKey'])
    if(product==None):
        return{
            'HttpCode' : '401',
            'Message' : 'Unexistent API key'
        }

    decrypted_data = decrypt_data(dataInfo['payload'],product)
    
    return {
        'HttpCode' : '200',
        'Message' : 'API key accepted'
    }