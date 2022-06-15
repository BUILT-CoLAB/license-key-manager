from numpy import product
from .models import Product, Key, Changelog, Registration, User, Client, Generallog
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
    print("Creating user (username='" + username + "', password='" + password + "') ", end="", flush=True)
    if( len( User.query.filter_by(name = username).all() ) > 0):
        print("USER ALREADY EXISTS! ... OK", flush=True)
        return
    print("USER DOES NOT EXIST --- ", end="", flush=True)
    newAccount = User(email = email, password = generate_password_hash(password), name = username)
    db.session.add(newAccount)
    db.session.commit()
    print("CREATED! ... OK", flush=True)

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
        
def createProduct(name, category, image, details, privateK, publicK, apiK):
    """
        Creates a new Product and stores it in the database.
    """
    newProduct = Product(name=name, category=category, image=image, details=details, privateK=privateK, publicK=publicK, apiK=apiK)
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
    if( not ( isinstance(productID, int) or productID.isnumeric() ) ):
        raise Exception("Invalid input - Denying database querying!")
    
    return db.engine.execute("""
    SELECT * FROM key JOIN (select id as cid, name from client) ON cid = KEY.clientid where Key.productid = """ + str(productID)
    )

def getKeysBySerialKey(serialKey, productID):
    print('ID-',productID)
    print('Serial-',serialKey)
    return Key.query.filter_by(serialkey = serialKey, productid=productID).first()

def createKey(productid, clientid, serialkey, maxdevices, expiryDate):
    """
        Creates a new Product and stores it in the database.
        The function returns the id of the newly created product.
    """
    newKey = Key(productid = productid, clientid = clientid, serialkey = serialkey, maxdevices = maxdevices, devices = 0, status = 0, expirydate = expiryDate)
    db.session.add(newKey)
    db.session.commit()
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


"""
//////////////////////////////////////////////////////////////////////////////
///////////  Registration Section ////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""

def createCustomer(name, email, phone, country):
    timestamp = int(time())
    newClient = Client(name = name, email = email, phone = phone, country = country, registrydate = timestamp)
    db.session.add(newClient)
    db.session.commit()

def modifyCustomer(clientid, name, email, phone, country):
    clientObj = Client.query.filter_by(id = clientid).first()
    clientObj.name = name
    clientObj.email = email
    clientObj.phone = phone
    clientObj.country = country
    db.session.commit()

def deleteCustomer(clientid):
    Client.query.filter_by(id = clientid).delete()

def getCustomer(customerName):
    """ 
        The following function queries the database for a given customer. If you wish to extract ALL 
        customers, the customerName should be '_ALL_'
    """
    if(customerName == '_ALL_'):
        return Client.query.all()
    return Client.query.filter(Client.name.contains(customerName)).all()