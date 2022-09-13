from ctypes import util
from pydoc import cli
from bin import databaseAPI as DBAPI
from bin.handlers import admins, customers,licenses,logs,products,utils,validation
from bin import keys
import pytest, time

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
    #this test fails due to lower level test fail
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

            # TODO: FIX the code bellow
            # Note: Each test automatically erases the database whenever a new test starts.
            # Also, avoid calling endpoints, such as 'licenses.changeLicenseState(data)' since the Flask won't have the required
            # payload to determine what's the current AdminAccount (and it will fail). Use the DBAPI if you wish to directly
            # manipulate the data in the database (or simply erase this test if you think it doesn't make sense)

            #assert len(DBAPI.getKeys(product.id)) >0
            #current_key = DBAPI.getKeys(product.id)[-1]
            #DBAPI.addRegistration()

            #one might not be what im looking for ...
            #dtemp = DBAPI.getKeyData(1)
            #DBAPI.addRegistration(1, 123, dtemp)
            #dtemp = DBAPI.getKeyData(1)
            #assert dtemp.devices ==1
            #data = {'licenseID': 1,'idclient' :'1','action':'RESET', 'maxdevices': '10','expirydate':'1000000' }
            #licenses.changeLicenseState(data)
            #datatemp = DBAPI.getKeyData(1)
            #assert datatemp.devices ==0


            #data = {'licenseID': current_key,'idclient' :'1','action':'DELETE', 'maxdevices': '10','expirydate':'1000000' }
            #licenses.changeLicenseState(data)
            #datatemp =  DBAPI.getKeyData(current_key)
            #assert datatemp == None


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

    
    customers.createCustomer(newCustomer)
    try:
        utils.validateMultiple_Customer(newCustomer.get('name'), newCustomer.get('email'), newCustomer.get('phone'))
    except Exception as exc:
        assert False, f"'newcustomer_validation' raised an exception {exc}"

    
