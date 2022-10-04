from src import database_api as DBAPI
from src.models import User, Product
from src import keys
from src.handlers import products
from werkzeug.security import check_password_hash


def test_newuser(auth, client, app):
    auth.login()
    with app.app_context():

        # GIVEN a User model
        # WHEN a new User is created
        # THEN check the email, hashed_password, and name fields are defined correctly
        # ALSO checks if user status is toggable

        DBAPI.generateUser('Marry', 'manuel2', 'marry32@gmail.com')
        user = DBAPI.obtainUser('Marry')
        assert user.email == 'marry32@gmail.com'
        assert user.name == 'Marry'
        assert user.password != 'manuel2'

        DBAPI.toggleUserStatus(1)
        assert user.disabled is False


def test_changePassword(auth, client, app):
    auth.login()
    with app.app_context():

       # GIVEN a User model
        # WHEN a  User changes its password
        # THEN check the  hashed_password is defined correctly

        DBAPI.generateUser('Marry', 'manuel2', 'marry32@gmail.com')
        user = DBAPI.obtainUser('Marry')
        DBAPI.changeUserPassword(user.id, 'newTestPass123')
        user = DBAPI.obtainUser('Marry')
        assert user.password != 'newTestPass123'
        assert check_password_hash(user.password, 'newTestPass123') is True


def test_new_old_user(auth, client, app):
    # GIVEN a Customer model
    # WHEN a new Customer is created
    # THEN check the email, hashed_password, and name fields are defined correctly
    # ALSO
    # WHEN a new Customer is selected for deletion
    # THEN check the none existance of the customer in the database
    auth.login()
    with app.app_context():
        DBAPI.createCustomer('Test', 'email@test.com',
                             '87654321', 'Mozambique')
        useer = DBAPI.getCustomer('Test')
        assert len(useer) > 0
        assert useer[0].name == 'Test'
        DBAPI.modifyCustomer(1, 'modTest', 'email@test.com',
                             '987654214', 'Mozambique')
        cust = DBAPI.getCustomerByID(1)
        assert cust is not None
        assert cust.name == 'modTest'

        DBAPI.deleteCustomer(1)
        cust = DBAPI.getCustomerByID(1)
        assert cust is None


def test_new_product(auth, client, app):
    # GIVEN a Product model
    # WHEN a new product is created
    # THEN check the increase of product,and category field defined correctly
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        assert len(product_keys) == 3
        productspec = {'name': 'Testing product',
                       'category': 'CAT 003SA',
                       'image': '',
                       'details': 'this product is for testing purposes only'
                       }
        count = DBAPI.getProductCount()

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get(
            'image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])
        assert product.category == 'CAT 003SA'
        assert DBAPI.getProductCount() == (count+1)

    #    ALSO
    # WHEN catefory of a product is editted
    # THEN check the category fields are defined correctly
        DBAPI.editProduct(product.id, 'Testing Product',
                          'CAT 004ZA', '', 'Improved testing version')
        productsame = DBAPI.getProductThroughAPI(product_keys[2])
        assert productsame.category == 'CAT 004ZA'
        assert productsame.details == 'Improved testing version'


def test_key_registration(auth, client, app):
    # GIVEN a Key model
    # WHEN a new lkey is created
    # THEN check the increase of product keys and fields defined correctly
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        productspec = {'name': 'Testing product',
                       'category': 'CAT 003SA',
                       'image': '',
                       'details': 'this product is for testing purposes only'
                       }

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get(
            'image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])

        serial = keys.generateSerialKey(10)
        keyidd = DBAPI.createKey(product.id, 1, serial, 3, 1000000000000000000)
        assert keyidd is not None

        # this shouldnt fail but does
        #all_keys = DBAPI.getKeys(product.id)
        #assert len(all_keys)>0

        keyy = DBAPI.getKeysBySerialKey(serial, product.id)
        assert keyidd == keyy.id
        assert keyy.devices == 0
        # ALSO
        # WHEN a new regestiration is created
        # THEN check the increase of devices and change in status keys
        DBAPI.addRegistration(keyy.id, 123, keyy)
        DBAPI.addRegistration(keyy.id, 234, keyy)
        keyy = DBAPI.getKeysBySerialKey(serial, product.id)
        assert keyy.devices == 2
        assert keyy.status == 1
        assert len(DBAPI.getKeyHWIDs(keyy.id)) == 2

        clientcount = DBAPI.getDistinctClients(product.id)
        assert clientcount == 1

        DBAPI.deleteRegistrationOfHWID(keyy.id, 234)
        keyy = DBAPI.getKeysBySerialKey(serial, product.id)
        assert keyy.devices == 1


def test__admin_logs(auth, client, app):
    # GIVEN a Log model
    # WHEN a new product is created
    # THEN check the increase of logs and fields defined correctly
    auth.login()
    with app.app_context():
        product_keys = keys.create_product_keys()
        productspec = {'name': 'Testing product',
                       'category': 'CAT 003SA',
                       'image': '',
                       'details': 'this product is for testing purposes only'
                       }

        product = DBAPI.createProduct(productspec.get('name'), productspec.get('category'), productspec.get(
            'image'), productspec.get('details'), product_keys[0], product_keys[1], product_keys[2])

        DBAPI.createCustomer('Test', 'email@test.com',
                             '87654321', 'Mozambique')
        adminAcc = DBAPI.getCustomer('Test')[0]
        logsnr = len(DBAPI.getUserLogs(adminAcc.id))
        DBAPI.submitLog(None, adminAcc.id, 'EditedProduct', '$$' +
                        str(adminAcc.name) + '$$ created product #' + str(product.id))

        logs = DBAPI.getUserLogs(adminAcc.id)
        assert len(logs) >= 1
        assert len(logs) == logsnr+1

        DBAPI.submitValidationLog(
            'OK', 'Key', '12.32.1234.221.1', 12342, 123432, 1234)
        result = DBAPI.queryValidationLogs()
        assert len(result) > 0
