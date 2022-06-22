from .models import Product, Key, Changelog, Registration, User, Client
from sqlalchemy import desc, func
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
    newAccount = User(email = email, password = generate_password_hash(password), name = username, timestamp = int(time()), owner = True)
    db.session.add(newAccount)
    db.session.commit()
    print("CREATED! ... OK", flush=True)

def obtainUser(username):
    """ 
        The following function simulates a SELECT statement to obtain the account that has the same username.
    """
    if(username == '_ALL_'):
        return User.query.all()
    return User.query.filter_by(name = username).first()

def createUser(email, username, password):
    newAccount = User(email = email, password = generate_password_hash(password), name = username, timestamp = int(time()))
    db.session.add(newAccount)
    db.session.commit()

def changeUserPassword(userid, password):
    selectedUser = User.query.filter_by(id = userid).first()
    selectedUser.password = generate_password_hash(password)
    db.session.commit()

def toggleUserStatus(userid):
    selectedUser = User.query.filter_by(id = userid).first()
    if(selectedUser.disabled == True):
        selectedUser.disabled = False
    else:
        selectedUser.disabled = True
    db.session.commit()

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

def getDistinctClients(productID):
    return db.session.query(Key.clientid).distinct().count()

def getProductsByPopularity():
    return db.engine.execute("""SELECT * FROM product LEFT JOIN (SELECT productid as licenses FROM Key) on licenses = product.id GROUP BY licenses ORDER BY licenses DESC""").fetchall()

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
    return newProduct

def editProduct(productid, name, category, image, details):
    """
        Edits an existing Product and saves the modifications in the database.
    """
    product = Product.query.filter_by(id = productid).first()
    product.name = name
    product.category = category
    product.image = image
    product.details = details
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
    ).fetchall()

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
    keyS = Key.query.filter_by(id=keyid).first()
    db.session.delete(keyS)
    db.session.commit()

def deleteKeysOfClient(clientid):
    keys = Key.query.filter_by(clientid = clientid).all()
    for key in keys:
        db.session.delete(key)
    db.session.commit()

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

def getKeyAndClient(keyid):
    if( not ( isinstance(keyid, int) or keyid.isnumeric() ) ):
        raise Exception("Invalid input - Denying database querying!")

    return db.engine.execute("""
    SELECT * FROM key JOIN (select id as cid, name from client) ON cid = key.clientid where Key.id = """ + str(keyid)
    ).fetchone()

"""
//////////////////////////////////////////////////////////////////////////////
///////////  ChangeLog Section ///////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""
def submitLog(keyid, userid, action, description):
    timestamp = int(time())
    if (keyid == None):
        newLog = Changelog(userid = userid, timestamp=timestamp, action = action, description = description)
    else:
        newLog = Changelog(keyID = keyid, userid = userid, timestamp=timestamp, action = action, description = description)
    db.session.add(newLog)
    db.session.commit()

def getKeyLogs(keyid):
    return db.session.query(Changelog, User.name).join(User, User.id == Changelog.userid).filter(Changelog.keyID == keyid).all()
    #return Changelog.query.filter_by(keyID = keyid).all()

def getUserLogs(userid):
    return Changelog.query.filter_by(userid = userid).all()

def queryLogs(userid, startdate, enddate):
    # db.session.query(Changelog, User.name).join(User, User.id == Changelog.userid).filter(Changelog.userid == userid).all()
    if( userid != -1 and startdate == -1 and enddate == -1 ):
        return db.session.query(Changelog).filter(Changelog.userid == userid).order_by(desc(Changelog.timestamp)).all()
    if( userid != -1 and startdate != -1 and enddate != -1 ):
        return db.session.query(Changelog).filter(Changelog.userid == userid and Changelog.timestamp >= startdate and Changelog.timestamp <= enddate).order_by(desc(Changelog.timestamp)).all()
    if( userid == -1 and startdate != -1 and enddate != -1 ):
        return db.session.query(Changelog).filter(Changelog.timestamp >= startdate and Changelog.timestamp <= enddate).order_by(desc(Changelog.timestamp)).all()
    if( userid == -1 and startdate == -1 and enddate == -1 ):
        return db.session.query(Changelog).order_by(desc(Changelog.timestamp)).all()
    return None

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
    clientS = Client.query.filter_by(id = clientid).first()
    db.session.delete(clientS)
    db.session.commit()

def getCustomer(customerName):
    """ 
        The following function queries the database for a given customer. If you wish to extract ALL 
        customers, the customerName should be '_ALL_'
    """
    if(customerName == '_ALL_'):
        return Client.query.all()
    return Client.query.filter(Client.name.contains(customerName)).all()