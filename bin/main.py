from flask import Blueprint, render_template, request
from sqlalchemy import text
from .models import Product
from Crypto.PublicKey import RSA
import random
import string
import json

from . import db
from . import _KEY_LENGTH_

main = Blueprint('main', __name__)

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
    productList = getProduct("")
    return render_template('cpanel.html', productList = productList)

@main.route('/cpanel/product/create', methods=['POST'])
def createProduct():
    dataInfo = request.get_json()
    print(dataInfo)

    # ################# Storage Data ####################
    AsyncKEYs = RSA.generate(1024)
    privateKey = AsyncKEYs.public_key().export_key('PEM')
    publicKey = AsyncKEYs.export_key('PEM')
    apiKey = generateAPIKey(_KEY_LENGTH_)
    name = dataInfo.get('name')
    logo = dataInfo.get('URL')
    # ###################################################

    newProduct = Product(name=name, logo=logo, privateK=privateKey, publicK=publicKey, apiK=apiKey)
    db.session.add(newProduct)
    db.session.commit()
    return "OKAY"

###########################################################################

@main.route('/cpanel/product/id/<productid>')
def productDisplay(productid):
    return render_template('product.html', prodID = productid)

@main.route('/cpanel/product/id/<productid>/createkey')
def createKey(productid):
    return render_template('product.html', prodID = productid)

def generateAPIKey(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    apiKey = ''.join(random.choice(characters) for i in range(length))
    return apiKey


######################### DATABASE API ###########################
def getProduct(searchString):
    return Product.query.all()