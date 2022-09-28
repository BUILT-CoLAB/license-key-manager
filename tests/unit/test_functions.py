from ctypes import util
from pydoc import cli
from bin import databaseAPI as DBAPI
from bin.handlers import admins, customers,licenses,logs,products,utils,validation
from bin import keys
from bin.models import User
import pytest, time
from datetime import datetime

def test_edits(auth, client,app ):
    #GIVEN a User and customer model
    #WHEN a new User and customer are edited
    #THEN check the email, hashed_password, and name fields were edited correctly
    auth.login()
    with app.app_context():
        newCustomer = { 'name':'Test Customer',
                        'email': 'test@customer.com',
                        'phone':'123456789',
                        'country':'PORTUGAL'
        }
        customers.createCustomer(newCustomer)
        current_user = DBAPI.getCustomer(newCustomer.get('name'))
        assert current_user[0].phone == newCustomer.get('phone')
        newCustomer = { 'name':'Test',
                        'email': 'test@customer.com',
                        'phone':'123456789',
                        'country':'PORTUGAL'
        }        
        customers.editCustomer(current_user[0].id, newCustomer)
        current_user = DBAPI.getCustomerByID(current_user[0].id)
        assert current_user.name == 'Test'


        product_keys = keys.create_product_keys()
        assert len(product_keys) == 3
        productspec = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
        }
        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get('image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])
        


def test_license(auth, client,app ):
    #GIVEN a license model
    #WHEN a license is edited
    #THEN check the changes happen correctly

    auth.login()
    with client:
        with app.app_context():
            product_keys = keys.create_product_keys()
            assert len(product_keys) == 3
            productspec = { 'name':'Testing product',
                    'category': 'CAT 003SA',
                    'image':'',
                    'details':'this product is for testing purposes only'
            }
            product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get('image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])
        
            try:
                DBAPI.createCustomer('Test Customer', 'test@customer.com', '123456789', 'PORTUGAL')
                DBAPI.createKey(product.id, 1, 'SDAFX-ADFAX', 10, int( time.time() ) + 200000 )
            except Exception as exc:
                assert False, f"'newlicense_validation' raised an exception when filling the Database {exc}"

            assert len(DBAPI.getKeys(product.id)) >0
            
            dtemp = DBAPI.getKeyData(1)
            DBAPI.addRegistration(1, 123, dtemp)
            DBAPI.addRegistration(1, 234, dtemp)
            dtemp = DBAPI.getKeyData(1)
            assert dtemp.devices ==2
            licenses.unlinkHardwareDevice(1,234)
            dtemp = DBAPI.getKeyData(1)
            assert dtemp.devices ==1
            data = {'licenseID': 1,'idclient' :'1','action':'RESET', 'maxdevices': '10','expirydate':'1000000' }
            licenses.changeLicenseState(data)
            dtemp = DBAPI.getKeyData(1)
            assert dtemp.devices ==0


            
            licens = DBAPI.getKeys(product.id)
            assert len(licens)>0
            current_key = licens[0]
            data = {'licenseID': 1,'idclient' :'1','action':'DELETE', 'maxdevices': '10','expirydate':'1000000' }
            licenses.changeLicenseState(data)
            licens = DBAPI.getKeys(1)
            assert licens != None
            assert len(licens) == 0
            

def test_keys(auth, client, app):
    auth.login()
    with client:
        with app.app_context():
            product_keys = keys.create_product_keys()
            assert len(product_keys) == 3
            assert product_keys[0] != product_keys[1]
            assert product_keys[1] != product_keys[2]
            assert product_keys[0] != product_keys[2]

            kk = keys.generateSerialKey(9)
            assert len(kk) == (9+1)



# def test_admin(auth, client, app):
#     admin_data = {
#         'email' : 'testing@admin1.com',
#         'username' : 'admin1',
#         'password' : 'administrator1'
#     }
#     admin_editdata = {
#         'email' : 'edit@admin.com',
#         'username' : 'admin1',
#         'password' : 'administrator1'
#     }
#     auth.login()
#     with client:
#         with app.app_context():
#             admins.createAdmin(admin_data)
#             user = User.query.filter_by(name = admin_data['username']).first()
#             assert user != None
#             assert user.email == admin_data['email']

#             admins.editAdmin(1, admin_editdata)

#             user = User.query.filter_by(name = admin_data['username']).first()
#             assert user != None
#             assert user.email == admin_editdata['email']

            
def test_utils():
    #GIVEN a human world
    #WHEN a data is inputed manually
    #THEN check correct raise of flags
    
    newCustomer = { 'name':'Test Customer',
                    'email': 'test@customer.com',
                    'phone':'123456789',
                     'country':'PORTUGAL'
    }
    with pytest.raises(Exception):
        utils.validateEmail('test@.com')
        utils.validateEmail('test.fail.com')
        utils.validateUsername('')
        utils.validateUsername('Test Fail')
        utils.validatePhone('abc123')
        utils.validateClientID(3)
        utils.validateMultiple_Customer(newCustomer.get('name'), newCustomer.get('email'), newCustomer.get('phone'))
        utils.validateMaxDevices('a')
        utils.validateMaxDevices(0)
        utils.validateExpiryDate(int( time.time() )-50 )

    
    customers.createCustomer(newCustomer)
    try:
        utils.validateMultiple_Customer(newCustomer.get('name'), newCustomer.get('email'), newCustomer.get('phone'))
    except Exception as exc:
        assert False, f"'newcustomer_validation' raised an exception {exc}"


