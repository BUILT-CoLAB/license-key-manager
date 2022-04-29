from .models import Product
from .models import Key
from .models import Changelog
from . import db
from time import time

"""
//////////////////////////////////////////////////////////////////////////////
///////////  Product Section /////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
"""

def getProduct(productName):
    """ The following function queries the database for a given product. If you wish to extract ALL 
        products, the productName should be '_ALL_'
    """
    if(productName == '_ALL_'):
        return Product.query.all()
    return Product.query.filter_by(name = productName).first()

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
"""


def getKeys(productID):
    """
        The following function queries the database for all keys belonging to a product. The product
        is identified by an ID.
    """
    return Key.query.filter_by(productid = productID).all()

def createKey(productid, customername, serialkey, maxdevices):
    """
        Creates a new Product and stores it in the database.
        The function returns the id of the newly created product.
    """
    newKey = Key(productid = productid, customername = customername, serialkey = serialkey, maxdevices = maxdevices, devices = 0, status = 0)
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

def resetKey(keyid):
    specificKey = Key.query.filter_by(id=keyid).first()
    specificKey.status = 0
    specificKey.devices = 0
    db.session.commit()

def getKeyData(keyid):
    return Key.query.filter_by(id=keyid).first()


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
