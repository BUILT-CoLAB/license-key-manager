from flask import Blueprint, render_template, request
from flask_httpauth import HTTPTokenAuth
from .models import Product
from . import databaseAPI as DBAPI
from .keys import create_product_keys, decrypt_data,generate_new_serial_key

main = Blueprint('main', __name__)

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    tokens = Product.query.filter_by(apiK=token).first()

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
    productList = DBAPI.getProduct('_ALL_')
    return render_template('cpanel.html', productList = productList)

@main.route('/cpanel/product/create', methods=['POST'])
def createProduct():
    dataInfo = request.get_json()

    # ################# Storage Data ####################    
    name = dataInfo.get('name')
    logo = dataInfo.get('URL')
    # ###################################################
    product_keys = create_product_keys()
    print(product_keys)
    DBAPI.createProduct(name, logo, product_keys[0],product_keys[1], product_keys[2])
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

    serialKey = generate_new_serial_key()
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


@main.route('/validate',methods=['POST'])
def validate_product():
    dataInfo = request.get_json()
    
    # Validating user with api key
    product = verify_token(dataInfo['apiKey'])
    if(product==None or product==[]):
        return{
            'HttpCode' : 401,
            'Message' : 'Unexistent API key'
        }

    decrypted_data = decrypt_data(dataInfo['payload'],product)
    
    keys = DBAPI.getKeysBySerialKey(decrypted_data[0],product.id)

    if(keys==None or keys==[]):
        return {
            'HttpCode' : 404,
            'Message' : 'Serial/License key not found'
        }
    print('Keys vector-',keys)
    print(keys.maxdevices)
    print(keys.devices)
    if(DBAPI.getDevice(decrypted_data[0],decrypted_data[1])==None):
        if(keys.devices <keys.maxdevices):#Add device to list of devices
            DBAPI.addDevice(decrypted_data[0],decrypted_data[1],keys)
            return {
                'HttpCode' : 200,
                'Message' : 'Device added to list'
            }
        else:#No more devices available
            return {
                'HttpCode' : 400,
                'Message' : 'Maximum number of devices reached for that license key'
            }
    else:#Device recognized - TODo- returning amount of time left for license key
        return {
            'HttpCode' : 200,
            'Message' : 'Everything okay'
        }

