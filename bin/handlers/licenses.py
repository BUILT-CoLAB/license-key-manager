from ..keys import generateSerialKey
from flask import render_template, request
from flask_login import current_user
from .. import databaseAPI as DBAPI
from . import utils as Utils
import json
from time import time

def displayLicense(licenseID):
    """
        Renders the display page of the License based on the indicated 'licenseID'.
        If an error occurs in any of the rendering steps, a 404-code page will be returned, indicating that the input is invalid or that a component does not exist.
    """
    if( not str(licenseID).isnumeric() ):
        return Utils.render404("License not found", "Sorry, but the license you have entered is invalid ...")
    
    try:
        license = DBAPI.getKeyAndClient(licenseID)
        if(license.status != 3 and license.expirydate < int(time())):
            print("Expiring key ...")
            DBAPI.applyExpirationState(license.id)
        changelog = DBAPI.getKeyLogs(licenseID)
        changelog.reverse()
        devices = DBAPI.getKeyHWIDs(licenseID)
    except Exception:
        return Utils.render404("Unknown Error", "Sorry, but there was an error acquiring the data from the database ...")

    if( license == None ):
        return Utils.render404("License not found", "Sorry, but the license you have entered does not exist ...")
    return render_template('license.html', license = license, changelog = changelog, devices = devices, mode = request.cookies.get('mode'))


def createLicense(productID, requestData):
    """
        Creates a license for the indicated productID and validates the data sent by the request (JSON format).
        The return comes in a JSON format, made out of a 'code' field and a 'message' field. The function will always return an error as a 'code' if the productID is invalid or does not exist, if the request data is also invalid or if an error occurs while handling the Database. 
    """
    adminAcc = current_user
    if( (not str(productID).isnumeric()) or DBAPI.getProductByID(productID) == None):
        return json.dumps({ 'code' : "ERROR", 'message' : "The product you have indicated is invalid or does not exist." })
    
    client = requestData.get('idclient')
    maxDevices = requestData.get('maxdevices')
    expiryDate = requestData.get('expirydate')

    validationR = Utils.validateMultiple_License(client, maxDevices, expiryDate)
    if not validationR == "":
        return json.dumps({ 'code' : "ERROR", 'message' : "Incorrect input: \n" + str(validationR) })

    try:
        serialKey = generateSerialKey(20)
        keyId = DBAPI.createKey(productID, int( client ), serialKey, int( maxDevices ), int( expiryDate ) )
        DBAPI.submitLog(keyId, adminAcc.id, 'CreatedKey', '$$' + str(adminAcc.name) + '$$ created license #' + str(keyId) + ' for product #' + str(productID))
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : "An error has occurred when storing the License in the database - #UNKNOWN ERROR!" })
    
    return json.dumps({ 'code' : "OKAY" })

def changeLicenseState(requestData):
    adminAcc = current_user
    licenseID = requestData.get('licenseID')
    action = requestData.get('action')
    if( not str(licenseID).isnumeric() or (action != 'SWITCHSTATE' and action != 'DELETE' and action != 'RESET') ):
        return json.dumps({ 'code' : "ERROR", 'message' : "The license and (or) the action request you have indicated is (are) invalid ..." })

    licenseObject = DBAPI.getKeyData(licenseID)
    if( licenseObject == None ):
        return json.dumps({ 'code' : "ERROR", 'message' : "The license you have indicated does not exist ..." })

    try:
        if action == 'SWITCHSTATE':
            if licenseObject.status != 2:
                DBAPI.setKeyState(licenseID, 2)
                DBAPI.submitLog(licenseID, adminAcc.id, 'RevokedKey', '$$' + str(adminAcc.name) + '$$ revoked license #' + str(licenseID))
            else:
                DBAPI.setKeyState(licenseID, getStatus(licenseObject.devices))
                DBAPI.submitLog(licenseID, adminAcc.id, 'ReactivatedKey', '$$' + str(adminAcc.name) + '$$ reactivated license #' + str(licenseID))

        if action == 'DELETE':
            DBAPI.deleteKey(licenseID)
            DBAPI.submitLog(None, adminAcc.id, 'DeletedKey', '$$' + str(adminAcc.name) + '$$ deleted the pre-existing license #' + str(licenseID))

        if action == 'RESET':
            DBAPI.resetKey(licenseID)
            DBAPI.submitLog(licenseID, adminAcc.id, 'ResetKey', '$$' + str(adminAcc.name) + '$$ reset license #' + str(licenseID))
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : "There was an error handling the state of the license - #UNKNOWN ERROR" })

    return json.dumps({ 'code' : "OKAY" })

def unlinkHardwareDevice(licenseID, hardwareID):
    adminAcc = current_user
    if( not str(licenseID).isnumeric() ):
        return json.dumps({ 'code' : "ERROR", 'message' : "The license you have entered is invalid ..." })

    try:
        DBAPI.deleteRegistrationOfHWID(licenseID, hardwareID)
        DBAPI.submitLog(licenseID, adminAcc.id, 'UnlinkedHWID$$$' + hardwareID, '$$' + str(adminAcc.name) + '$$ removed Hardware ' + str(hardwareID) + ' from license #' + str(licenseID))
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : "There was an error managing the state of the license - #UNKNOWN ERROR" })
    
    return json.dumps({ 'code' : "OKAY" })

# Auxiliary Method
def getStatus(activeDevices):
    if(activeDevices > 0):
        return 1
    return 0