from .. import databaseAPI as DBAPI
from ..keys import decrypt_data
from flask import request
import json
import math
import time

def handleValidation(requestData):
    response = validate(requestData)
    generateLogContents(requestData, response)
    return json.dumps(response)

def validate(requestData):
    # STEP 1 :: Validate the existence of an API Key
    product = DBAPI.getProductThroughAPI( requestData.get('apiKey') )
    if(product==None or product==[]):
        return responseMessage(401, 'ERR_API_KEY', 'ERROR :: The API Key you have entered is invalid. The validation request did not go through.')
    # ##############################################################################

    # STEP 2 :: Extract the descrypted data
    decryptedData = decrypt_data( requestData.get('payload') , product)
    # The data in the decryptedData section is organized as:
    # decryptedData[0] - Serial Key
    # decryptedData[1] - Hardware ID
    # ##############################################################################

    # STEP 3 :: Validate the Serial Key by matching it to an existing License object
    keyObject = DBAPI.getKeysBySerialKey(decryptedData[0], product.id)
    if(keyObject==None or keyObject==[]):
        return responseMessage(401, 'ERR_SERIAL_KEY', 'ERROR :: The Serial Key you have entered is invalid. The validation request went through but was rejected.', decryptedData)
    # ##############################################################################

    if(DBAPI.getRegistration(keyObject.id, decryptedData[1]) == None):
        return handleNonExistingState(keyObject, decryptedData)
    else:
        return handleExistingState(keyObject, decryptedData)

def handleExistingState(keyObject, decryptedData):
    """
        Handles the situation where a device is already linked to the specified license. 
        In this situation, the method merely checks whether or not the license is still valid.
    """
    if( validateExpirationDate( keyObject.expirydate ) ):
        return responseMessage(200, 'OKAY', 'OKAY STATUS :: This device is still registered and everything is okay.', decryptedData, keyObject.expirydate)
    else:
        DBAPI.applyExpirationState(keyObject.id)
        return responseMessage(400, 'ERR_KEY_EXPIRED', 'ERROR :: This license is no longer valid.', decryptedData, keyObject.expirydate)

def handleNonExistingState(keyObject, decryptedData):
    """
        Handles the situation where a device is not yet linked to the specified license. 
        Multiple checks are done before the license is authorized for validation.
    """

    # STEP 1 :: Validate the status of the License (if it's revoked/disabled, then interrupt the validation with an error)
    if(keyObject.status == 2):
        return responseMessage(403, 'ERR_KEY_REVOKED', 'ERROR :: The key was revoked. Your request was valid but the license is disabled until further notice.', decryptedData, keyObject.expirydate)

    # STEP 2 :: Check if the License has expired. If that's the case, then the validation should be interrupted with an error.
    if( not validateExpirationDate( keyObject.expirydate ) ):
        DBAPI.applyExpirationState(keyObject.id)
        return responseMessage(400, 'ERR_KEY_EXPIRED', 'ERROR :: This license is no longer valid and will not admit any new devices.', decryptedData, keyObject.expirydate)
    
    # STEP 3 :: Check if the License's device list can hold more devices.
    if(keyObject.devices == keyObject.maxdevices):
        return responseMessage(400, 'ERR_KEY_DEVICES_FULL', 'ERROR :: The maximum number of devices for this license key has been reached.', decryptedData, keyObject.expirydate)

    # If all steps above go through, then we accept the validation
    DBAPI.addRegistration(keyObject.id, decryptedData[1], keyObject)
    return responseMessage(201, 'SUCCESS', 'SUCCESS :: Your registration was successful!', decryptedData, keyObject.expirydate)


# Utility Functions
def responseMessage(HTTPCode = 200, ResponseCode = 'OKAY', Message = 'Everything is okay (DEFAULT RESPONSE)', decryptedData = [None, None], expirationDate = None):
    """
        Creates a JSON string that contains all the individual components of a standard response.
    """
    return {
        'HttpCode' : str(HTTPCode),
        'Message' : str(Message),
        'Code' : str(ResponseCode),
        'SerialKey' : decryptedData[0],
        'HardwareID' : decryptedData[1],
        'ExpirationDate' : int( -1 ) if expirationDate == None else int( expirationDate )
    }

def generateLogContents(requestData, responseMessage):
    # ################################################# SET-UP DATABASE FIELDS
    result = 'ERROR' if ('ERR' in responseMessage['Code']) else 'SUCCESS'
    code = str( responseMessage['Code'] )
    apiKey = str( requestData.get('apiKey') )
    serialKey = str( str( responseMessage['SerialKey'] ) )
    hardwareID = str( responseMessage['HardwareID'] )
    ipaddress = str( request.access_route[-1] )
    # ########################################################################
    DBAPI.submitValidationLog( result, code, ipaddress, apiKey, serialKey, hardwareID )


####### MERELY AUXILIARY FUNCTIONS
def validateExpirationDate(expiryDate):
    """
        Verifies the state of the current expiration date. 
        If the license is still valid, the method returns True. Otherwise, it returns false.
    """
    if( expiryDate == 0 ):
        return True
    if( math.floor( time.time() ) > int(expiryDate) ):
        return False
    return True