from pydoc import cli
from bin import databaseAPI as DBAPI
from bin.handlers import admins, customers,licenses,logs,products,utils,validation
from bin import keys

def test_edits(auth, client,app ):
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
            
            data = {'idclient' :'1', 'maxdevices': '10','expirydate':'1000000' }
            licenses.createLicense(product.id, data)
            
            #this is impossible to test upon failure of function getKeys

            # assert len(DBAPI.getKeys(product.id)) >0
            # current_key = DBAPI.getKeys(product.id)[-1]
            # DBAPI.addRegistration()
            

            #one might not be what im looking for ...
            # dtemp = DBAPI.getKeyData(1)
            # DBAPI.addRegistration(1, 123, dtemp)
            # dtemp = DBAPI.getKeyData(1)
            # assert dtemp.devices ==1
            # data = {'licenseID': 1,'idclient' :'1','action':'RESET', 'maxdevices': '10','expirydate':'1000000' }
            # licenses.changeLicenseState(data)
            # datatemp = DBAPI.getKeyData(1)
            # assert datatemp.devices ==0

            

            # data = {'licenseID': 1,'idclient' :'1','action':'SWITCHSTATE', 'maxdevices': '10','expirydate':'1000000' }
            # licenses.changeLicenseState(data)

            
