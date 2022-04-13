from flask import Blueprint, render_template, request
from sqlalchemy import text
from .models import Product
import random
import string
import json
from . import db
from . import _KEY_LENGTH_
from .keys import create_product

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

    db.session.add(create_product(name,logo))
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