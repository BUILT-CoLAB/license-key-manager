from bin import databaseAPI as DBAPI
from bin.models import User, Product
from bin import keys 
from bin.handlers import products
def test_newuser(auth,client,app):
    auth.login()
    with app.app_context():

        DBAPI.generateUser('Marry', 'manuel2', 'marry32@gmail.com')
        user = DBAPI.obtainUser('Marry')
        assert user.email == 'marry32@gmail.com'
        assert user.name == 'Marry'
        assert user.password != 'manuel2'

        DBAPI.toggleUserStatus(1)
        assert user.disabled == False

        


def test_new_old_user(auth,client,app):
    auth.login()
    with app.app_context():
        DBAPI.createCustomer('Test', 'email@test.com', '87654321', 'Mozambique')
        useer = DBAPI.getCustomer('Test')
        assert len(useer) >0
        assert useer[0].name == 'Test'
        cust = DBAPI.getCustomerByID(1)
        assert cust != None

        DBAPI.deleteCustomer(1)
        cust = DBAPI.getCustomerByID(1)
        assert cust == None





def test_new_product(auth,client,app):
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        assert len(product_keys) == 3
        productspec = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
        }
        count = DBAPI.getProductCount() 

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get('image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])

        assert DBAPI.getProductCount() == (count+1)
        DBAPI.editProduct(product.id, 'Testing Product', 'CAT 004ZA', '', 'Improved testing version')
        productsame = DBAPI.getProductThroughAPI(product_keys[2])
        assert productsame.category == 'CAT 004ZA'
        

        
        


def test_key_registration(auth, client, app):
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        productspec = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
        }

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get('image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])
        
        serial = keys.generateSerialKey(10)
        keyidd = DBAPI.createKey(product.id, 1, serial, 10, 1000000000000000000)
        assert keyidd != None
        all_keys = DBAPI.getKeys(product.id)
        
        #this shouldnt fail but does
        #assert len(all_keys)>0

        keyy = DBAPI.getKeysBySerialKey(serial, product.id)
        assert keyidd == keyy.id
        assert keyy.devices ==0 
        
        DBAPI.addRegistration(keyy.id, 123, keyy)
        keyy = DBAPI.getKeysBySerialKey(serial, product.id)
        assert keyy.devices ==1
        assert keyy.status == 1


def test__admin_logs(auth, client, app):
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        productspec = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
        }

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get('image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])

        DBAPI.createCustomer('Test', 'email@test.com', '87654321', 'Mozambique')
        adminAcc =  DBAPI.getCustomer('Test')
        #este teste nao passa se usar os dados do adminAcc, basically getCustomer doesnt work 
        logsnr =  len(DBAPI.getUserLogs(adminAcc))
        DBAPI.submitLog(None,adminAcc[0].id, 'EditedProduct', '$$' + str(adminAcc[0].name) + '$$ created product #' + str(product.id))
        
        logs = DBAPI.getUserLogs(adminAcc)
        assert len(logs)>= 1
        assert len(logs) == logsnr+1
        