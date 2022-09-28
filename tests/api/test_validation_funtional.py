import base64
import json
from plistlib import load
from sre_constants import SUCCESS
from uuid import uuid4
import pytest
from bin import databaseAPI,db
from bin.models import Product,Client, Key, Registration
from bin.keys import create_product_keys, generateSerialKey
from datetime import datetime
from time import time
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

@pytest.fixture
def created_product_1(app):
    with app.app_context():
        product_keys = create_product_keys()
        product = Product(name = 'Testing product',category = 'CAT 003SA', image = '',details = 'Testing product only', privateK = product_keys[0], publicK = product_keys[1], apiK = product_keys[2])
        db.session.add(product)
        db.session.commit()
        final_product = Product.query.filter_by(id = product.id).first()
    
    yield final_product
    with app.app_context():
        db.session.delete(final_product)
        db.session.commit()

@pytest.fixture
def created_product_2(app):
    with app.app_context():
        product_keys = create_product_keys()
        product = Product(name = 'Testing product 2',category = 'CAT 003SB', image = '',details = 'Testing product 2 only', privateK = product_keys[0], publicK = product_keys[1], apiK = product_keys[2])
        db.session.add(product)
        db.session.commit()
        final_product = Product.query.filter_by(id = product.id).first()
    
    yield final_product
    with app.app_context():
        db.session.delete(final_product)
        db.session.commit()

@pytest.fixture()
def created_customer(app):
    with app.app_context():
        newClient = Client(name = "Test Customer", email = 'test@customer.com', phone = '123456789', country = 'PORTUGAL', registrydate = int (time()))
        db.session.add(newClient)
        db.session.commit()
        final_client = Client.query.filter_by(id=newClient.id).first()
    yield final_client
    with app.app_context():
        databaseAPI.deleteCustomer(final_client.id)

@pytest.fixture
def created_license(app,created_customer,created_product_1):
    with app.app_context():
        serialKey = generateSerialKey(20)
        keyId = databaseAPI.createKey(created_product_1.id, created_customer.id, serialKey, 2, int(datetime.timestamp(datetime.fromisoformat('2023-10-10'))) )
        key = Key.query.filter_by(id=keyId).first()
    
    yield key
    with app.app_context():
        final_key = Key.query.filter_by(id=key.id).first()
        if(final_key != None):
            db.session.delete(final_key)
            db.session.commit()

@pytest.fixture
def created_expired_license(app,created_customer,created_product_1):
    with app.app_context():
        serialKey = generateSerialKey(20)
        keyId = databaseAPI.createKey(created_product_1.id, created_customer.id, serialKey, 1, int(datetime.timestamp(datetime.fromisoformat('2021-10-10'))) )
        key = Key.query.filter_by(id=keyId).first()
    
    yield key
    with app.app_context():
        final_key = Key.query.filter_by(id=key.id).first()
        if(final_key != None):
            db.session.delete(final_key)
            db.session.commit()

@pytest.fixture
def add_device_valid(app,created_customer,created_product_1,created_license):
    with app.app_context():
        hw_id = str(uuid4())
        key = databaseAPI.getKeyData(created_license.id)
        databaseAPI.addRegistration(key.id, hw_id,key)
        registration = Registration.query.first()

    yield registration
    with app.app_context():
        final_registration  = Registration.query.first()
        if(final_registration != None):
            databaseAPI.deleteRegistrationOfHWID(created_license.id,hw_id)

@pytest.fixture
def add_device_expired(app,created_customer,created_product_1,created_expired_license):
    with app.app_context():
        hw_id = str(uuid4())
        key = databaseAPI.getKeyData(created_expired_license.id)
        databaseAPI.addRegistration(key.id, hw_id,key)
        registration = Registration.query.first()

    yield registration
    with app.app_context():
        final_registration  = Registration.query.first()
        if(final_registration != None):
            databaseAPI.deleteRegistrationOfHWID(created_expired_license.id,hw_id)

def test_device_validation(auth,client,app,created_product_1,created_customer,created_license):
    """Tests if API successfully validates a product license

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_license : Key
        License ORM object added to the database before the test (fixture)

    Returns
    -------
    """

    hw_id = str(uuid4())
    public_key =serialization.load_pem_public_key(created_product_1.publicK)
    plaintexts = bytes(created_license.serialkey + ':' + hw_id, 'utf-8')
    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload = base64.b64encode(payload).decode('utf-8')
    json_info = {
        'apiKey' : created_product_1.apiK,
        'payload' : final_payload
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code == 200
    loaded_response = json.loads(response.data)
    assert loaded_response['HttpCode'] == "201"
    assert loaded_response['Message'] == "SUCCESS :: Your registration was successful!"
    assert loaded_response['Code'] == "SUCCESS"

    with app.app_context():
        registration = databaseAPI.getRegistration(created_license.id,hw_id)
        assert registration != None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 1
        assert license.maxdevices >= license.devices
    

def test_max_devices_fail(auth,client,app,created_product_1,created_customer,created_license):
    """Tests if API successfully validates licenses until max devices number reached

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_license : Key
        License ORM object added to the database before the test (fixture)

    Returns
    -------
    """
        
    hw_id_1 = str(uuid4())
    hw_id_2 = str(uuid4())
    hw_id_3 = str(uuid4())

    public_key =serialization.load_pem_public_key(created_product_1.publicK)
    plaintexts1 = bytes(created_license.serialkey + ':' + hw_id_1, 'utf-8')
    plaintexts2 = bytes(created_license.serialkey + ':' + hw_id_2, 'utf-8')
    plaintexts3 = bytes(created_license.serialkey + ':' + hw_id_3, 'utf-8')
    #Encrypting first payload
    payload1 = public_key.encrypt(
        plaintexts1,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    #Encrypting second payload
    payload2 = public_key.encrypt(
        plaintexts2,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    #Encrypting third payload
    payload3 = public_key.encrypt(
        plaintexts3,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload_1 = base64.b64encode(payload1).decode('utf-8')
    final_payload_2 = base64.b64encode(payload2).decode('utf-8')
    final_payload_3 = base64.b64encode(payload3).decode('utf-8')

    #Sending first request 
    json_info = {
        'apiKey' : created_product_1.apiK,
        'payload' : final_payload_1
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code == 200
    loaded_response = json.loads(response.data)
    assert loaded_response['HttpCode'] == "201"
    assert loaded_response['Message'] == "SUCCESS :: Your registration was successful!"
    assert loaded_response['Code'] == "SUCCESS"

    with app.app_context():
        registration = databaseAPI.getRegistration(created_license.id,hw_id_1)
        assert registration != None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 1
        assert license.maxdevices >= license.devices

        #Sending second request 
        json_info = {
            'apiKey' : created_product_1.apiK,
            'payload' : final_payload_2
        }

        response = client.post("/api/v1/validate",json = json_info)
        assert response.status_code == 200
        loaded_response = json.loads(response.data)
        assert loaded_response['HttpCode'] == "201"
        assert loaded_response['Message'] == "SUCCESS :: Your registration was successful!"
        assert loaded_response['Code'] == "SUCCESS"

        registration = databaseAPI.getRegistration(created_license.id,hw_id_2)
        assert registration != None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 2
        assert license.maxdevices == license.devices

        #Sending third request 
        json_info = {   
            'apiKey' : created_product_1.apiK,
            'payload' : final_payload_3
        }

        response = client.post("/api/v1/validate",json = json_info)
        assert response.status_code == 200
        loaded_response = json.loads(response.data)
        assert loaded_response['HttpCode'] == "400"
        assert loaded_response['Message'] == "ERROR :: The maximum number of devices for this license key has been reached."
        assert loaded_response['Code'] == "ERR_KEY_DEVICES_FULL"

        registration = databaseAPI.getRegistration(created_license.id,hw_id_3)
        assert registration == None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 2
        assert license.maxdevices == license.devices


def test_device_validation_on_expired_license(auth,client,app,created_product_1,created_customer,created_expired_license):
    """Tests if API successfully rejects validation due to expiration date

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_expired_license : Key
        License (expired) ORM object added to the database before the test (fixture)

    Returns
    -------
    """

    hw_id = str(uuid4())
    public_key =serialization.load_pem_public_key(created_product_1.publicK)
    plaintexts = bytes(created_expired_license.serialkey + ':' + hw_id, 'utf-8')
    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload = base64.b64encode(payload).decode('utf-8')
    json_info = {
        'apiKey' : created_product_1.apiK,
        'payload' : final_payload
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code == 200
    loaded_response = json.loads(response.data)
    assert loaded_response['HttpCode'] == "400"
    assert loaded_response['Message'] == "ERROR :: This license is no longer valid and will not admit any new devices."
    assert loaded_response['Code'] == "ERR_KEY_EXPIRED"

    with app.app_context():
        registration = databaseAPI.getRegistration(created_expired_license.id,hw_id)
        assert registration == None
        license = databaseAPI.getKeyData(created_expired_license.id)
        assert license.devices == 0
        assert license.maxdevices >= license.devices


def test_device_revalidation_on_valid_license(auth,client,app,created_product_1,created_customer,created_license,add_device_valid):
    """Tests if API successfully revalidates

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_license : Key
        License ORM object added to the database before the test (fixture)

    add_device_valid : Registration
        Registration ORM object added to the database before the test (fixture)

    Returns
    -------
    """
    with app.app_context():
        # asserts that devices number is 1
        registration = databaseAPI.getRegistration(created_license.id,add_device_valid.hardwareID)
        assert registration != None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 1
        assert license.maxdevices >= license.devices
        
        #Tries revalidation
        public_key =serialization.load_pem_public_key(created_product_1.publicK)
        plaintexts = bytes(created_license.serialkey + ':' + add_device_valid.hardwareID, 'utf-8')
        payload = public_key.encrypt(
            plaintexts,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        final_payload = base64.b64encode(payload).decode('utf-8')
        json_info = {
            'apiKey' : created_product_1.apiK,
            'payload' : final_payload
        }

        response = client.post("/api/v1/validate",json = json_info)
        assert response.status_code == 200
        loaded_response = json.loads(response.data)
        assert loaded_response['HttpCode'] == "200"
        assert loaded_response['Message'] == "OKAY STATUS :: This device is still registered and everything is okay."
        assert loaded_response['Code'] == "OKAY"

    
        registration = databaseAPI.getRegistration(created_license.id,add_device_valid.hardwareID)
        assert registration != None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 1
        assert license.maxdevices >= license.devices


def test_device_revalidation_on_expired_license(auth,client,app,created_product_1,created_customer,created_expired_license,add_device_expired):
    """Tests if API successfully revalidates

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_expired_license : Key
        License (expired) ORM object added to the database before the test (fixture)

    add_device_expired : Registration
        Registration (expired) ORM object added to the database before the test (fixture)

    Returns
    -------
    """
    with app.app_context():
        # asserts that devices number is 1
        registration = databaseAPI.getRegistration(created_expired_license.id,add_device_expired.hardwareID)
        assert registration != None
        license = databaseAPI.getKeyData(created_expired_license.id)
        assert license.devices == 1
        assert license.maxdevices >= license.devices
        
        #Tries revalidation
        public_key =serialization.load_pem_public_key(created_product_1.publicK)
        plaintexts = bytes(created_expired_license.serialkey + ':' + add_device_expired.hardwareID, 'utf-8')
        payload = public_key.encrypt(
            plaintexts,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        final_payload = base64.b64encode(payload).decode('utf-8')
        json_info = {
            'apiKey' : created_product_1.apiK,
            'payload' : final_payload
        }

        response = client.post("/api/v1/validate",json = json_info)
        assert response.status_code == 200
        loaded_response = json.loads(response.data)
        assert loaded_response['HttpCode'] == "400"
        assert loaded_response['Message'] == "ERROR :: This license is no longer valid."
        assert loaded_response['Code'] == "ERR_KEY_EXPIRED"

    
        registration = databaseAPI.getRegistration(created_expired_license.id,add_device_expired.hardwareID)
        assert registration != None
        license = databaseAPI.getKeyData(created_expired_license.id)
        assert license.devices == 1
        assert license.status == 3
        assert license.maxdevices >= license.devices


def test_invalid_validation_input_serial_key(auth,client,app,created_product_1,created_customer):
    """Tests if API rejects invalid inputs for validation

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    Returns
    -------
    """

    license_key = "failed_serial_key"
    public_key =serialization.load_pem_public_key(created_product_1.publicK)
    plaintexts = bytes(license_key + ':' + str(uuid4()), 'utf-8')
    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload = base64.b64encode(payload).decode('utf-8')
    json_info = {
        'apiKey' : created_product_1.apiK,
        'payload' : final_payload
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code == 200
    loaded_response = json.loads(response.data)
    assert loaded_response['HttpCode'] == "401"
    assert loaded_response['Message'] == "ERROR :: The Serial Key you have entered is invalid. The validation request went through but was rejected."
    assert loaded_response['Code'] == "ERR_SERIAL_KEY"

    with app.app_context():    
        registration = databaseAPI.getKeysBySerialKey(license_key,created_product_1.id)
        assert registration == None
        license = Key.query.filter_by(serialkey = license_key).first()
        assert license == None


def test_invalid_validation_input_api_key(auth,client,app,created_product_1,created_customer,created_license):
    """Tests if API rejects invalid inputs for validation - api key

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_license : Key
        License ORM object added to the database before the test (fixture)

    Returns
    -------
    """
    
    public_key =serialization.load_pem_public_key(created_product_1.publicK)
    plaintexts = bytes(created_license.serialkey + ':' + str(uuid4()), 'utf-8')
    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload = base64.b64encode(payload).decode('utf-8')
    json_info = {
        'apiKey' : 'errorKey',
        'payload' : final_payload
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code == 200
    loaded_response = json.loads(response.data)
    assert loaded_response['HttpCode'] == "401"
    assert loaded_response['Message'] == "ERROR :: The API Key you have entered is invalid. The validation request did not go through."
    assert loaded_response['Code'] == "ERR_API_KEY"

    with app.app_context():    
        registration = databaseAPI.getKeyHWIDs(created_license.id)
        assert registration == []
        license = databaseAPI.getKeyData(created_license.id)
        assert license != None
        assert license.productid == created_product_1.id
        assert license.devices == 0


def test_bad_encryption(auth,client,app,created_product_1,created_product_2,created_customer,created_license):
    """Tests if API rejects data encrypted using another products public key and if server does not crash

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_product_1 : Product
        Product (1) ORM object added to the database before the test (fixture)

    created_product_2 : Product
        Product (2) ORM object added to the database before the test (fixture)

    created_customer : Customer
        Customer ORM object added to the database before the test (fixture)

    created_license : Key
        License ORM object added to the database before the test (fixture)

    Returns
    -------
    """
    
    
    hw_id = str(uuid4())
    # Using created_product_2 public key instead of created_product_1
    public_key =serialization.load_pem_public_key(created_product_2.publicK)
    plaintexts = bytes(created_license.serialkey + ':' + hw_id, 'utf-8')
    payload = public_key.encrypt(
        plaintexts,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    final_payload = base64.b64encode(payload).decode('utf-8')
    json_info = {
        'apiKey' : created_product_1.apiK,
        'payload' : final_payload
    }

    response = client.post("/api/v1/validate",json = json_info)
    assert response.status_code != 500

    with app.app_context():
        registration = databaseAPI.getRegistration(created_license.id,hw_id)
        assert registration == None
        license = databaseAPI.getKeyData(created_license.id)
        assert license.devices == 0
        assert license.maxdevices >= license.devices