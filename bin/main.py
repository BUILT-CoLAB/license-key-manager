from flask import Blueprint, render_template, request
from flask_httpauth import HTTPTokenAuth
from .models import Product
from . import databaseAPI as DBAPI
from .keys import create_product_keys, decrypt_data, generateSerialKey

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
    return render_template('product.html', prodID = productid, keyList = keyList, pcontent = productContent, pubKey = productContent.publicK.decode('utf-8'))

@main.route('/cpanel/keydata/id/<keyid>')
def keyDataDisplay(keyid):
    keyData = DBAPI.getKeyData(keyid)
    logData = DBAPI.getKeyLogs(keyid)
    registrations = DBAPI.getKeyHWIDs(keyid)
    logData.reverse()
    return render_template('keydata.html', keyData = keyData, logData = logData, registrations = registrations)

@main.route('/cpanel/product/id/<productid>/createkey', methods=['POST'])
def createKey(productid):
    dataInfo = request.get_json()
    print(dataInfo)

    serialKey = generateSerialKey(20)
    keyId = DBAPI.createKey(productid, dataInfo.get('name'), dataInfo.get('email'), dataInfo.get('phoneNumber'), serialKey, dataInfo.get('maxDevices'))
    DBAPI.submitLog(keyId, 'Created')
    return "OKAY"

@main.route('/cpanel/editkeys', methods=['POST'])
def updateKeyState():
    dataInfo = request.get_json()
    print(dataInfo)

    # Handle "REVOKE" Request
    if(dataInfo.get('action') == 'SWITCHSTATE'):
        for keyID in dataInfo.get('keyList'):       # For this operation only 1 key is given
            keyData = DBAPI.getKeyData(keyID)
            if keyData.status != 2:
                DBAPI.setKeyState(keyID, 2)
                DBAPI.submitLog(keyID, 'Revoked')
            else:
                DBAPI.setKeyState(keyID, getStatus(keyData.devices))
                DBAPI.submitLog(keyID, 'Reactivated')
            
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
    
    # 1st Step: Validate user with API key.
    product = verify_token(dataInfo['apiKey'])
    if(product==None or product==[]):
        return{
            'HttpCode' : 401,
            'Message' : 'Unexistent API key'
        }
    # #####################################

    decryptedData = decrypt_data(dataInfo['payload'], product)

    # decryptedData[0] - Serial Key
    # decryptedData[1] - Hardware ID

    keyObject = DBAPI.getKeysBySerialKey(decryptedData[0], product.id)

    if(keyObject==None or keyObject==[]):
        return {
            'HttpCode' : 404,
            'Message' : 'Serial/License key not found'
        }

    print("[NOTE] Request received to authenticate HWID '" + str(decryptedData[1]) + "' with serial key '" + str(keyObject.id) + "'.")
    print("[NOTE] Maximum number of devices: " + str(keyObject.maxdevices) + ".")
    print("[NOTE] Current number of devices (pre-validation): " + str(keyObject.devices) + ".")


    if(DBAPI.getRegistration(keyObject.id, decryptedData[1]) == None):
        # Check if the key is revoked
        if(keyObject.status == 2):
            return {
                'HttpCode' : 403,
                'Message' : 'Forbbiden access :: Key revoked! Your hardware was not registered.'
            }

        # Check if the number of devices if okay
        if(keyObject.devices < keyObject.maxdevices): # Add device to list of devices
            DBAPI.addRegistration(keyObject.id, decryptedData[1], keyObject)
            return {
                'HttpCode' : 201,
                'Message' : 'Registration successful'
            }
        else:   # No more devices available
            return {
                'HttpCode' : 400,
                'Message' : 'Maximum number of devices reached for that license key'
            }
    else:
        return {
            'HttpCode' : 200,
            'Message' : 'Your device is registered.',
            'KeyStatus' : keyObject.id
        }






# Auxiliary Methods
def getStatus(activeDevices):
    if(activeDevices > 0):
        return 1
    return 0