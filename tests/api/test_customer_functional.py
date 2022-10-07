import json
from src import database_api, db
from src.models import Client
import pytest
from time import time


@pytest.fixture
def created_customer(app):
    with app.app_context():
        newClient = Client(name="Test Customer", email='test@customer.com',
                           phone='123456789', country='PORTUGAL', registrydate=int(time()))
        db.session.add(newClient)
        db.session.commit()
        final_client = Client.query.filter_by(id=newClient.id).first()
    yield final_client
    with app.app_context():
        test_if_exists = Client.query.filter_by(id=newClient.id).first()
        if(test_if_exists is not None):
            database_api.deleteCustomer(test_if_exists.id)


def test_creation(auth, client, app):
    """Tests if API successfully creates a customer database entry

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
    newCustomer = {
        'name': 'Test Customer',
        'email': 'test@customer.com',
        'phone': '123456789',
        'country': 'PORTUGAL'
    }

    response = client.post("/customers/create", json=newCustomer)
    assert response.status_code == 200

    with app.app_context():
        customer = database_api.getCustomerByID(1)
        assert customer is not None
        assert customer.id == 1
        assert customer.name == newCustomer['name']
        assert customer.country == newCustomer['country']
        assert customer.phone == newCustomer['phone']
        assert customer.email == newCustomer['email']


def test_edit(auth, client, app, created_customer):
    """Tests if API successfully edits a customer database entry

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_customer : Client
        Client orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login()
    changedCustomer = {
        'name': 'Final Customer',
        'email': 'test@finalcustomer.com',
        'phone': '123456789',
        'country': 'SENEGAL'
    }

    # Tries to edit an unexistent customer
    response = client.post(
        "/customers/edit/"+str(created_customer.id+1), json=changedCustomer)
    assert response.status_code != 200
    parsed_json = json.loads(response.data)
    assert parsed_json['code'] == "ERROR"
    assert parsed_json['message'] == "The database failed to edit the customer data - #UNKNOWN ERROR"

    # Tries to edit an existent customer
    response = client.post(
        "/customers/edit/"+str(created_customer.id), json=changedCustomer)
    assert response.status_code == 200
    with app.app_context():
        customer = database_api.getCustomerByID(1)
        assert customer is not None
        assert created_customer != changedCustomer
        assert customer.id == 1
        assert customer.name == changedCustomer['name']
        assert customer.country == changedCustomer['country']
        assert customer.phone == changedCustomer['phone']
        assert customer.email == changedCustomer['email']


def test_delete(auth, client, app, created_customer):
    """Tests if API successfully deletes a customer database entry

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app :  FlaskApp
        The app needed to query the Database

    created_customer : Client
        Client orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login()
    with app.app_context():
        customer = database_api.getCustomerByID(created_customer.id)
        assert customer is not None

        # Tries to delete an unexistent customer
        response = client.post("/customers/delete/"+str(created_customer.id+1))
        assert response.status_code != 200
        json_loaded = json.loads(response.data)
        assert json_loaded['code'] == "ERROR"
        assert json_loaded['message'] == "The database failed to delete the customer - #UNKNOWN ERROR"

        # Tries to delete an existent customer
        response = client.post("/customers/delete/"+str(created_customer.id))
        assert response.status_code == 200
        json_loaded = json.loads(response.data)
        assert json_loaded['code'] == "OKAY"

        customer = database_api.getCustomerByID(created_customer.id)
        assert customer is None
