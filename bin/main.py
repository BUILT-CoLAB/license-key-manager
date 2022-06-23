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

from .handlers import admins as AdminHandler, changelogs as ChangelogHandler, customers as CustomerHandler, products as ProductHandler, licenses as LicenseHandler

main = Blueprint('main', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    tokens = Product.query.filter_by(apiK=token).first()
    return tokens

@main.route('/')
def index():
    return render_template('index.html', mode = request.cookies.get('mode'))

@main.route('/tutorial')
@login_required
def tutorial():
    return render_template('tutorial.html', mode = request.cookies.get('mode'))

@main.route('/dashboard')
@login_required
def cpanel():
    productList = DBAPI.getProductsByPopularity()
    activated, awaitingApproval = DBAPI.getKeyStatistics()
    if( activated == 0 and awaitingApproval == 0 ):
        ratio = 100
    else:
        ratio = ( activated / (activated + awaitingApproval) ) * 100
    return render_template('cpanel.html', productList = productList, activated = activated, awaitingApproval = awaitingApproval, ratio = round(ratio), mode = request.cookies.get('mode'))



###########################################################################
########### PRODUCT HANDLING
###########################################################################
@main.route('/products')
@login_required
def products():
    return ProductHandler.displayProductList()

@main.route('/products/id/<productid>')
@login_required
def productDisplay(productid):
    return ProductHandler.displayProduct( productid )

@main.route('/products/create', methods=['POST'])
@login_required
def createProduct():
    return ProductHandler.createProduct( request.get_json() )

@main.route('/products/edit', methods=['POST'])
@login_required
def editProduct():
    return ProductHandler.editProduct( request.get_json() )





###########################################################################
########### CUSTOMER HANDLING
###########################################################################
@main.route('/customers')
@login_required
def customers():
    return CustomerHandler.displayCustomers()

@main.route('/customers/create', methods=['POST'])
@login_required
def createCustomer():
    return CustomerHandler.createCustomer( request.get_json() )

@main.route('/customers/edit/<customerid>', methods=['POST'])
@login_required
def modifyCustomer(customerid):
    return CustomerHandler.editCustomer(customerid, request.get_json() )

@main.route('/customers/delete/<customerid>', methods=['POST'])
@login_required
def deleteCustomer(customerid):
    return CustomerHandler.deleteCustomer(customerid)



###########################################################################
########### LICENSE KEY HANDLING
###########################################################################
@main.route('/product/<productid>/createlicense', methods=['POST'])
@login_required
def createLicense(productid):
    return LicenseHandler.createLicense( productid, request.get_json() )

@main.route('/licenses/<licenseid>')
@login_required
def licenseDisplay(licenseid):
    return LicenseHandler.displayLicense(licenseid)

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
    return ChangelogHandler.displayChangelog()

@main.route('/changelog/query')
@login_required
def getlogs():
    return ChangelogHandler.queryLogs( request.args.to_dict() )


###########################################################################
########### ADMINISTRATOR ACCOUNTS - HANDLING
###########################################################################
@main.route('/admins')
@login_required
def adminsDisplay():
    return AdminHandler.displayAdminPage()

@main.route('/admins/create',methods=['POST'])
@login_required
def adminCreate():
    return AdminHandler.createAdmin( request.get_json() )

@main.route('/admins/<userid>/edit',methods=['POST'])
@login_required
def adminEdit(userid):
    return AdminHandler.editAdmin(userid, request.get_json() )

@main.route('/admins/<userid>/togglestatus',methods=['POST'])
@login_required
def adminToggleStatus(userid):
    return AdminHandler.toggleAdminStatus(userid)




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
