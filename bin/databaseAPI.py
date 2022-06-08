from .models import Product, Key, Changelog, Registration, User
from werkzeug.security import generate_password_hash
from . import db
from time import time


"""
//////////////////////////////////////////////////////////////////////////////
///////////  Admin Section ///////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""
def generateUser(username, password, email):
    """ 
        The following function creates a user account with the indicated data.
    """
    print("Creating user (username='" + username + "', password='" + password + "') ", end="")
    if( len( User.query.filter_by(name = username).all() ) > 0):
        print("USER ALREADY EXISTS! ... OK")
        return
    print("USER DOES NOT EXIST --- ", end="")
    newAccount = User(email = email, password = generate_password_hash(password), name = username)
    db.session.add(newAccount)
    db.session.commit()
    print("CREATED! ... OK", end="")

def obtainUser(username):
    """ 
        The following function simulates a SELECT statement to obtain the account that has the same username.
    """
    return User.query.filter_by(name = username).first()



"""
//////////////////////////////////////////////////////////////////////////////
///////////  Product Section /////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""

def getProduct(productName):
    """ 
        The following function queries the database for a given product. If you wish to extract ALL 
        products, the productName should be '_ALL_'
    """
    if(productName == '_ALL_'):
        return Product.query.all()
    return Product.query.filter(Product.name.contains(productName)).all()

def getProductByID(productID):
    """ 
        The following function queries the database for a given product by its ID.
    """
    return Product.query.filter_by(id = productID).first()
        
def createProduct(name, logo, privateK, publicK, apiK):
    """
        Creates a new Product and stores it in the database.
    """
    newProduct = Product(name=name, logo=logo, privateK=privateK, publicK=publicK, apiK=apiK)
    db.session.add(newProduct)
    db.session.commit()


"""
//////////////////////////////////////////////////////////////////////////////
///////////  Key Section /////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

KEY STATUS:
0 --> Awaiting Approval
1 --> Active
2 --> Revoked
"""

def getKeys(productID):
    """
        The following function queries the database for all keys belonging to a product. The product
        is identified by an ID.
    """
    return Key.query.filter_by(productid = productID).all()

def getKeysBySerialKey(serialKey, productID):
    print('ID-',productID)
    print('Serial-',serialKey)
    return Key.query.filter_by(serialkey = serialKey, productid=productID).first()

def createKey(productid, customername, email, phonenumber, serialkey, maxdevices, expiryDate):
    """
        Creates a new Product and stores it in the database.
        The function returns the id of the newly created product.
    """
    newKey = Key(productid = productid, customername = customername, customeremail = email, customerphone = phonenumber, serialkey = serialkey, maxdevices = maxdevices, devices = 0, status = 0, expirydate = expiryDate)
    
    db.session.add(newKey)
    db.session.commit()
    print(newKey.id)
    return newKey.id

def setKeyState(keyid, newState):
    specificKey = Key.query.filter_by(id=keyid).first()
    specificKey.status = int(newState)
    db.session.commit()

def deleteKey(keyid):
    Key.query.filter_by(id=keyid).delete()
    db.session.commit()
    deleteLogs(keyid)
    deleteRegistrationsOfKey(keyid)

def resetKey(keyid):
    specificKey = Key.query.filter_by(id=keyid).first()
    deleteRegistrationsOfKey(keyid)
    specificKey.status = 0
    specificKey.devices = 0
    db.session.commit()

def getKeyData(keyid):
    return Key.query.filter_by(id=keyid).first()

def getKeyStatistics():
    activated = Key.query.filter_by(status=1).count()
    awaitingApproval = Key.query.filter_by(status=0).count()
    return activated, awaitingApproval
"""
//////////////////////////////////////////////////////////////////////////////
///////////  ChangeLog Section ///////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""

def submitLog(keyid, action):
    timestamp = int(time())
    newLog = Changelog(keyID=keyid, timestamp=timestamp, action=action)
    db.session.add(newLog)
    db.session.commit()

def getKeyLogs(keyid):
    return Changelog.query.filter_by(keyID=keyid).all()

def deleteLogs(keyid):
    Changelog.query.filter_by(keyID=keyid).delete()
    db.session.commit()


"""
//////////////////////////////////////////////////////////////////////////////
///////////  Registration Section ////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""

def getRegistration(keyID, hardwareID):
    return Registration.query.filter_by(keyID = keyID, hardwareID = hardwareID).first()

def getKeyHWIDs(keyID):
    return Registration.query.filter_by(keyID = keyID).all()

def deleteRegistrationsOfKey(keyID):
    Registration.query.filter_by(keyID = keyID).delete()
    db.session.commit()

def deleteRegistrationOfHWID(keyID, hardwareID):
    Registration.query.filter_by(keyID = keyID, hardwareID = hardwareID).delete()
    originalKey = getKeyData(keyID)
    originalKey.devices = originalKey.devices - 1
    db.session.commit()

def addRegistration(keyID, hardwareID, keyObject):
    # Add a new Registration that links a KeyID with an HardwareID
    newDevice = Registration(keyID = keyID, hardwareID = hardwareID)
    db.session.add(newDevice)

    # Update the number of active devices of a license key and its state
    newActiveDevices = keyObject.devices + 1
    keyObject.devices = newActiveDevices
    if(keyObject.status != 1):
        keyObject.status = 1

    # Submit all changes
    db.session.commit()

    # Log the changes
    submitLog(keyID, 'Activated')