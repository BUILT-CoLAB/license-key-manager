from datetime import datetime
import json
from math import prod
from time import time
from uuid import uuid4
from bin import databaseAPI
import pytest
from bin import db
from bin.keys import create_product_keys, generateSerialKey
from flask_login import current_user

from bin.models import Client, Key, Product, Registration

@pytest.fixture()
def create_customer(app):
    with app.app_context():
        newClient = Client(name = "Test Customer", email = 'test@customer.com', phone = '123456789', country = 'PORTUGAL', registrydate = int (time()))
        db.session.add(newClient)
        db.session.commit()
        final_client = Client.query.filter_by(id=newClient.id).first()
    yield final_client
    with app.app_context():
        databaseAPI.deleteCustomer(final_client.id)

@pytest.fixture
def create_product(app):
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
def create_license(app,create_customer,create_product):
    with app.app_context():
        serialKey = generateSerialKey(20)
        keyId = databaseAPI.createKey(create_product.id, create_customer.id, serialKey, 10, int(datetime.timestamp(datetime.fromisoformat('2023-10-10'))) )
        key = Key.query.filter_by(id=keyId).first()
    
    yield key
    with app.app_context():
        final_key = Key.query.filter_by(id=key.id).first()
        if(final_key != None):
            db.session.delete(final_key)
            db.session.commit()

@pytest.fixture
def add_device(app,create_customer,create_product,create_license):
    with app.app_context():
        hw_id = "AAAA-BBBB-CCCC-DDDD-EEEE"
        key = databaseAPI.getKeyData(create_license.id)
        databaseAPI.addRegistration(key.id, hw_id,key)
        registration = Registration.query.first()

    yield registration
    with app.app_context():
        final_registration  = Registration.query.first()
        if(final_registration != None):
            databaseAPI.deleteRegistrationOfHWID(create_license.id,hw_id)
        

def test_creation(auth,client,app,create_product,create_customer):
    """Tests if API successfully creates a license

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()
    expiryDate = datetime.timestamp(datetime.fromisoformat('2023-10-10'))
    
    license = { 
        'idclient':create_customer.id,
        'maxdevices': 4,
        'expirydate': expiryDate
    }
    endpoint = "/product/"+str(create_product.id)+"/createlicense"
    response = client.post(endpoint,json=license)
    assert response.status_code == 200
    
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 1
        assert licenses[0].id == 1
        assert licenses[0].productid == 1
        assert licenses[0].clientid == license['idclient']
        assert licenses[0].maxdevices == license['maxdevices']
        assert licenses[0].expirydate == int(license['expirydate'])
        assert licenses[0].status == 0
        assert licenses[0].devices == 0


def test_delete_without_associated_device(app,auth,client,create_license):
    """Tests if API successfully deletes a license when there is no associated devices

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()    
    license_edit = {
        'licenseID' : create_license.id,
        'action' : 'DELETE'
    }
    response = client.post("/licenses/editkeys",json=license_edit)
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 0


def test_delete_with_associated_device(app,auth,client,create_license):
    """Tests if API successfully deletes a license when there are associated devices

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()    
    license_edit = {
        'licenseID' : create_license.id,
        'action' : 'DELETE'
    }
    response = client.post("/licenses/editkeys",json=license_edit)
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        licenses = databaseAPI.getKeys(create_license.id)
        assert licenses != None
        assert len(licenses) == 0

        registrations = databaseAPI.getKeyHWIDs(create_license.id)
        assert registrations != None
        assert len(registrations) == 0


def test_switch_state_no_active_devices(auth,client,app,create_customer,create_product,create_license):
    """Tests if API successfully switches license state. License has no devices associated

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()    
    
    license_edit = {
        'licenseID' : create_license.id,
        'action' : 'SWITCHSTATE'
    }
    response = client.post("/licenses/editkeys",json=license_edit)
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 1
        assert licenses[0].status == 2

        response = client.post("/licenses/editkeys",json=license_edit)
        assert response.status_code == 200
        assert json.loads(response.data)['code'] == "OKAY"

        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 1
        assert licenses[0].status == 0


def test_switch_state_with_active_devices(auth,client,app,create_customer,create_product,create_license,add_device):
    """Tests if API successfully switches license state when there is 1 associated device

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()       

    # Tries to change state of existent license
    license_edit = {
        'licenseID' : create_license.id,
        'action' : 'SWITCHSTATE'
    }
    response = client.post("/licenses/editkeys",json=license_edit)
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 1
        assert licenses[0].status == 2

        response = client.post("/licenses/editkeys",json=license_edit)
        assert response.status_code == 200
        assert json.loads(response.data)['code'] == "OKAY"

        licenses = databaseAPI.getKeys(1)
        assert licenses != None
        assert len(licenses) == 1
        assert licenses[0].status == 1

@pytest.mark.parametrize(('licenseID', 'action','message'), (
    (1+1, 'SWITCHSTATE', 'The license you have indicated does not exist ...'),
    ('test', 'SWITCHSTATE', 'The license and (or) the action request you have indicated is (are) invalid ...'),
    (1, 'test', 'The license and (or) the action request you have indicated is (are) invalid ...'),
    (1+1, 'test', 'The license and (or) the action request you have indicated is (are) invalid ...')
))
def test_invalid_switch_state(auth,client,app,create_customer,create_product,create_license,add_device,licenseID,action,message):
    """Tests if API rejects invalid switches license state requests

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()       
    
    # Tries to change state with invalid licenseID
    invalid_license_edit = {
        'licenseID' : licenseID,
        'action' : action
    }
    response = client.post("/licenses/editkeys",json=invalid_license_edit)
    # RESPONSE STATUS CODE SHOULD NOT BE 200.
    # THE SERVER SENDS 200 BECAUSE JSON.DUMPS DOES NOT THINK AN ERROR OCURRED
    # THAT NEEDS TO BE CHANGED. THROW EXCEPTION OR SEND AN DIFFERENT HTTP CODE
    assert response.status_code != 200
    loaded_json = json.loads(response.data)
    assert loaded_json['code'] == "ERROR"
    assert loaded_json['message'] == message


def test_unlinking_device(auth,client,app,create_customer,create_product,create_license,add_device):
    """Tests if API successfully unlinks device from license

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()       

    json_body = {
        'hardwareID' : add_device.hardwareID
    }
    string_endpoint = "licenses/"+str(create_license.id)+"/removedevice"
    response = client.post(string_endpoint,json=json_body)
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        registrations = databaseAPI.getRegistration(create_license.id,add_device.hardwareID)
        assert registrations == None

@pytest.mark.parametrize(('licenseID', 'hardwareID','message'), (
    (1, 'test', 'There was an error managing the state of the license - #UNKNOWN ERROR'),
    ('test', "AAAA-BBBB-CCCC-DDDD-EEEE", 'The license you have entered is invalid ...'),
    (1+1, "AAAA-BBBB-CCCC-DDDD-EEEE", 'There was an error managing the state of the license - #UNKNOWN ERROR'),
    (1+1, 'test', 'There was an error managing the state of the license - #UNKNOWN ERROR')
))
def test_invalid_unlinking_device(auth,client,app,create_customer,create_product,create_license,add_device,licenseID,hardwareID,message):
    """Tests if API rejects invalid unlink requests

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    Returns
    -------
    """

    auth.login()       

    json_body = {
        'hardwareID' : hardwareID
    }
    string_endpoint = "licenses/"+str(licenseID)+"/removedevice"
    response = client.post(string_endpoint,json=json_body)    
    loaded_json= json.loads(response.data)
    assert loaded_json['code'] == "ERROR"
    assert loaded_json['message'] == message
    # RESPONSE STATUS CODE SHOULD NOT BE 200.
    # THE SERVER SENDS 200 BECAUSE JSON.DUMPS DOES NOT THINK AN ERROR OCURRED
    # THAT NEEDS TO BE CHANGED. THROW EXCEPTION OR SEND AN DIFFERENT HTTP CODE
    assert response.status_code != 200

    with app.app_context():
        registrations = databaseAPI.getRegistration(create_license.id,add_device.hardwareID)
        assert registrations != None
        assert registrations.id == add_device.id
