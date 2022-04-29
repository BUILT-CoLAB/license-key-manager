from flask import Blueprint, render_template, request
from sqlalchemy import text
from Crypto.PublicKey import RSA
import random
import string
import json

from . import databaseAPI as DBAPI
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
    productList = DBAPI.getProduct('_ALL_')
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

    DBAPI.createProduct(name, logo, privateKey, publicKey, apiKey)
    return "OKAY"

###########################################################################

@main.route('/cpanel/product/id/<productid>')
def productDisplay(productid):
    keyList = DBAPI.getKeys(productid)
    productContent = DBAPI.getProductByID(productid)
    return render_template('product.html', prodID = productid, keyList = keyList, pcontent = productContent)

@main.route('/cpanel/keydata/id/<keyid>')
def keyDataDisplay(keyid):
    keyData = DBAPI.getKeyData(keyid)
    logData = DBAPI.getKeyLogs(keyid)
    logData.reverse()
    return render_template('keydata.html', keyData = keyData, logData = logData)

@main.route('/cpanel/product/id/<productid>/createkey', methods=['POST'])
def createKey(productid):
    dataInfo = request.get_json()
    print(dataInfo)

    serialKey = generateSerialKey(20)
    keyId = DBAPI.createKey(productid, dataInfo.get('name'), serialKey, dataInfo.get('maxDevices'))
    DBAPI.submitLog(keyId, 'Created')
    return "OKAY"

"""
KEY STATUS:
0 --> Awaiting Approval
1 --> Active
2 --> Revoked
"""

@main.route('/cpanel/editkeys', methods=['POST'])
def updateKeyState():
    dataInfo = request.get_json()
    print(dataInfo)

    # Handle "REVOKE" Request
    if(dataInfo.get('action') == 'REVOKE'):
        for keyID in dataInfo.get('keyList'):
            DBAPI.setKeyState(keyID, 2)
            DBAPI.submitLog(keyID, 'Revoked')
            
    # Handle "DELETE" Request
    if(dataInfo.get('action') == 'DELETE'):
        for keyID in dataInfo.get('keyList'):
            DBAPI.deleteKey(keyID)

    # Handle "RESET" Request
    if(dataInfo.get('action') == 'RESET'):
        for keyID in dataInfo.get('keyList'):
            DBAPI.resetKey(keyID)
            DBAPI.submitLog(keyID, 'Reset')

    return "OK"

def generateAPIKey(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    apiKey = ''.join(random.choice(characters) for i in range(length))
    return apiKey

def generateSerialKey(length):
    characters = string.ascii_uppercase + string.digits
    serialKey = ''
    for i in range(length):
        if(i % 5 == 0 and i != 0):
            serialKey += '-'
        serialKey += random.choice(characters)
    return serialKey