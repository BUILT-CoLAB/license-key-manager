from ..keys import generateSerialKey
from flask import render_template, request
from flask_login import current_user
from .. import databaseAPI as DBAPI
from . import utils as Utils
import json

def displayLicense(licenseID):
    if( not str(licenseID).isnumeric() ):
        return Utils.render404("License not found", "Sorry, but the license you have entered is invalid ...")
    
    license = DBAPI.getKeyAndClient(licenseID)
    changelog = DBAPI.getKeyLogs(licenseID)
    changelog.reverse()
    devices = DBAPI.getKeyHWIDs(licenseID)

    if( license == None ):
        return Utils.render404("License not found", "Sorry, but the license you have entered does not exist ...")
    return render_template('license.html', license = license, changelog = changelog, devices = devices, mode = request.cookies.get('mode'))


def createLicense(productID, requestData):
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
