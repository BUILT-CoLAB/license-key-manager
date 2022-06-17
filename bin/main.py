from flask import Blueprint, render_template, request
from flask_httpauth import HTTPTokenAuth
from flask_login import login_required
from .models import Product
from . import databaseAPI as DBAPI
from .auth import getCurrentUser
from .keys import create_product_keys, decrypt_data, generateSerialKey
import json
import time
import math

main = Blueprint('main', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    tokens = Product.query.filter_by(apiK=token).first()
    return tokens

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/tutorial')
@login_required
def tutorial():
    return render_template('tutorial.html')

@main.route('/dashboard')
@login_required
def cpanel():
    productList = DBAPI.getProductsByPopularity()
    activated, awaitingApproval = DBAPI.getKeyStatistics()
    if( activated == 0 and awaitingApproval == 0 ):
        ratio = 100
    else:
        ratio = ( activated / (activated + awaitingApproval) ) * 100
    return render_template('cpanel.html', productList = productList, activated = activated, awaitingApproval = awaitingApproval, ratio = round(ratio) )



###########################################################################
########### PRODUCT HANDLING
###########################################################################
@main.route('/products')
@login_required
def products():
    products = DBAPI.getProduct('_ALL_')
    return render_template('products.html', products = products)

@main.route('/products/id/<productid>')
@login_required
def productDisplay(productid):
    licenses = DBAPI.getKeys(productid)
    productContent = DBAPI.getProductByID(productid)
    customers = DBAPI.getCustomer('_ALL_')
    return render_template('product.html', licenses = licenses, product = productContent, pubKey = productContent.publicK.decode('utf-8'), customers = customers)

@main.route('/products/create', methods=['POST'])
@login_required
def createProduct():
    adminAcc = getCurrentUser()
    dataInfo = request.get_json()

    # ################# Storage Data ####################    
    name = dataInfo.get('name')
    category = dataInfo.get('category')
    image = dataInfo.get('image')
    details = dataInfo.get('details')
    # ###################################################

    product_keys = create_product_keys()
    DBAPI.createProduct(name, category, image, details, product_keys[0], product_keys[1], product_keys[2])
    DBAPI.submitLog(None, adminAcc.id, 'EditedProduct', '$$' + str(adminAcc.name) + '$$ created product #' + str(id))
    return "SUCCESS"

@main.route('/products/edit', methods=['POST'])
@login_required
def editProduct():
    adminAcc = getCurrentUser()
    dataInfo = request.get_json()

    # ################# Storage Data ####################  
    id = dataInfo.get('id')
    name = dataInfo.get('name')
    category = dataInfo.get('category')
    image = dataInfo.get('image')
    details = dataInfo.get('details')
    # ###################################################

    DBAPI.editProduct( int(id), name, category, image, details )
    DBAPI.submitLog(None, adminAcc.id, 'EditedProduct', '$$' + str(adminAcc.name) + '$$ modified the data details of product #' + str(id))
    return "SUCCESS"





###########################################################################
########### CUSTOMER HANDLING
###########################################################################
@main.route('/customers')
@login_required
def customers():
    customers = DBAPI.getCustomer('_ALL_')
    return render_template('customers.html', customers = customers)

@main.route('/customers/create', methods=['POST'])
@login_required
def createCustomer():
    dataInfo = request.get_json()
    # ################# Storage Data ####################    
    name = dataInfo.get('name')
    email = dataInfo.get('email')
    phone = dataInfo.get('phone')
    country = dataInfo.get('country')
    # ###################################################
    DBAPI.createCustomer(name, email, phone, country)
    return "SUCCESS"

@main.route('/customers/edit/<keyid>', methods=['POST'])
@login_required
def modifyCustomer(keyid):
    dataInfo = request.get_json()
    # ################# Storage Data ####################    
    name = dataInfo.get('name')
    email = dataInfo.get('email')
    phone = dataInfo.get('phone')
    country = dataInfo.get('country')
    # ###################################################
    DBAPI.modifyCustomer(keyid, name, email, phone, country)
    return "SUCCESS"

@main.route('/customers/delete/<keyid>', methods=['POST'])
@login_required
def deleteCustomer(keyid):
    DBAPI.deleteCustomer(keyid)
    return "SUCCESS"



###########################################################################
########### LICENSE KEY HANDLING
###########################################################################
@main.route('/product/<productid>/createlicense', methods=['POST'])
@login_required
def createLicense(productid):
    adminAcc = getCurrentUser()
    dataInfo = request.get_json()
    serialKey = generateSerialKey(20)
    keyId = DBAPI.createKey(productid, int( dataInfo.get('idclient') ), serialKey, int( dataInfo.get('maxdevices') ), int( dataInfo.get('expirydate') ) )
    DBAPI.submitLog(keyId, adminAcc.id, 'CreatedKey', '$$' + str(adminAcc.name) + '$$ created license #' + str(keyId) + ' for product #' + str(productid))
    return "OKAY"

@main.route('/licenses/<licenseid>')
@login_required
def licenseDisplay(licenseid):
    license = DBAPI.getKeyAndClient(licenseid)
    changelog = DBAPI.getKeyLogs(licenseid)
    changelog.reverse()
    devices = DBAPI.getKeyHWIDs(licenseid)
    return render_template('license.html', license = license, changelog = changelog, devices = devices)

@main.route('/licenses/editkeys', methods=['POST'])
@login_required
def updateKeyState():
    dataInfo = request.get_json()
    adminAcc = getCurrentUser()
    print(dataInfo)

    # Handle "REVOKE" Request
    if(dataInfo.get('action') == 'SWITCHSTATE'):
        for keyID in dataInfo.get('keyList'):       # For this operation only 1 key is given
            keyData = DBAPI.getKeyData(keyID)
            if keyData.status != 2:
                DBAPI.setKeyState(keyID, 2)
                DBAPI.submitLog(keyID, adminAcc.id, 'RevokedKey', '$$' + str(adminAcc.name) + '$$ revoked license #' + str(keyID))
            else:
                DBAPI.setKeyState(keyID, getStatus(keyData.devices))
                DBAPI.submitLog(keyID, adminAcc.id, 'ReactivatedKey', '$$' + str(adminAcc.name) + '$$ reactivated license #' + str(keyID))
            
    # Handle "DELETE" Request
    if(dataInfo.get('action') == 'DELETE'):
        for keyID in dataInfo.get('keyList'):
            DBAPI.deleteKey(keyID)
            DBAPI.submitLog(None, adminAcc.id, 'DeletedKey', '$$' + str(adminAcc.name) + '$$ deleted the pre-existing license #' + str(keyID))

    # Handle "RESET" Request
    if(dataInfo.get('action') == 'RESET'):
        for keyID in dataInfo.get('keyList'):
            DBAPI.resetKey(keyID)
            DBAPI.submitLog(keyID, adminAcc.id, 'ResetKey', '$$' + str(adminAcc.name) + '$$ reset license #' + str(keyID))

    return "OK"

@main.route('/licenses/<keyid>/removedevice', methods=['POST'])
@login_required
def hardwareIDRemove(keyid):
    adminAcc = getCurrentUser()
    dataInfo = request.get_json()
    DBAPI.deleteRegistrationOfHWID(keyid, dataInfo.get('hardwareID'))
    DBAPI.submitLog(keyid, adminAcc.id, 'UnlinkedHWID$$$' + dataInfo.get('hardwareID'), '$$' + str(adminAcc.name) + '$$ removed Hardware ' + str(dataInfo.get('hardwareID')) + ' from license #' + str(keyid))
    return "OK"



###########################################################################
########### CHANGELOG HANDLING
###########################################################################
@main.route('/changelog')
@login_required
def changelog():
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('changelog.html', users = userList)

@main.route('/changelog/query')
@login_required
def getlogs():
    parameters = request.args.to_dict()
    changelogs = DBAPI.queryLogs( int(parameters.get('adminid')), int(parameters.get('datestart')), int(parameters.get('dateend')) )
    changelog = []
    for log in changelogs:
        changelog.append({'adminid' : log.userid, 'timestamp' : log.timestamp, 'description' : log.description})
    return json.dumps(changelog)


###########################################################################
########### ADMINISTRATOR ACCOUNTS - HANDLING
###########################################################################
@main.route('/admins')
@login_required
def adminsDisplay():
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('users.html', users = userList)

@main.route('/admins/create',methods=['POST'])
@login_required
def adminCreate():
    dataInfo = request.get_json()
    DBAPI.createUser(dataInfo.get('email'), dataInfo.get('username'), dataInfo.get('password'))
    return "SUCCESS"

@main.route('/admins/<userid>/edit',methods=['POST'])
@login_required
def adminEdit(userid):
    dataInfo = request.get_json()
    DBAPI.changeUserPassword( userid, dataInfo.get('password') )
    return "SUCCESS"

@main.route('/admins/<userid>/togglestatus',methods=['POST'])
@login_required
def adminToggleStatus(userid):
    DBAPI.toggleUserStatus(userid)
    return "SUCCESS"




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

    isStillValid = isDateWithin(keyObject.expirydate)

    if(DBAPI.getRegistration(keyObject.id, decryptedData[1]) == None):
        # Check if the key is revoked
        if(keyObject.status == 2):
            return {
                'HttpCode' : 403,
                'Message' : 'Forbbiden access :: Key revoked! Your hardware was not registered.',
                'Code' : 'KEY_REVOKED'
            }

        # Check if the key is still valid
        if( not isStillValid ):
            return {
                'HttpCode' : 400,
                'Message' : 'Registration denied :: The key has expired.',
                'Code' : 'KEY_EXPIRED'
            }

        # Check if the number of devices if okay
        if(keyObject.devices < keyObject.maxdevices): # Add device to list of devices
            DBAPI.addRegistration(keyObject.id, decryptedData[1], keyObject)
            return {
                'HttpCode' : 201,
                'Message' : 'Registration successful',
                'Code' : 'SUCCESS',
                'ExpiryTimestamp' : keyObject.expirydate
            }
        else:   # No more devices available
            return {
                'HttpCode' : 400,
                'Message' : 'Maximum number of devices reached for that license key',
                'Code' : 'KEY_DEVICES_FULL'
            }
    else:
        if( not isStillValid):
            return {
                'HttpCode' : 400,
                'Message' : 'Your registration has expired. Update required.',
                'Code' : 'KEY_EXPIRED'
            }
        else:
            return {
                'HttpCode' : 200,
                'Message' : 'Your device is still registered.',
                'KeyStatus' : keyObject.id,
                'Code' : 'OKAY'
            }

# Auxiliary Methods
def getStatus(activeDevices):
    if(activeDevices > 0):
        return 1
    return 0

def isDateWithin(limitDate):
    if( limitDate == 0 ):   # Life-time license
        return True
    if( math.floor( time.time() ) > int(limitDate) ):
        return False
    return True
    
