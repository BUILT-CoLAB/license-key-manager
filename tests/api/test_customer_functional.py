from bin import databaseAPI

def test_creation(auth,client,app):
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
    with app.app_context():
        customer = databaseAPI.getCustomerByID(1)
        assert customer == None
    
        newCustomer = { 'name':'Test Customer',
                        'email': 'test@customer.com',
                        'phone':'123456789',
                        'country':'PORTUGAL'
        }

        response = client.post("/customers/create",json=newCustomer)
        assert response.status_code == 200

        customer = databaseAPI.getCustomerByID(1)
        assert customer != None
        assert customer.id == 1
        assert customer.name == newCustomer['name']
        assert customer.country == newCustomer['country']
        assert customer.phone == newCustomer['phone']
        assert customer.email == newCustomer['email']


def test_edit(auth,client,app):
    """Tests if API successfully edits a customer database entry

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
    with app.app_context():    
        newCustomer = { 
            'name':'Test Customer',
            'email': 'test@customer.com',
            'phone':'123456789',
            'country':'PORTUGAL'
        }

        response = client.post("/customers/create",json=newCustomer)
        assert response.status_code == 200

        changedCustomer = {
            'name':'Final Customer',
            'email': 'test@finalcustomer.com',
            'phone':'123456789',
            'country':'SENEGAL'
        }

        response = client.post("/customers/edit/1",json=changedCustomer)
        assert response.status_code == 200

        customer = databaseAPI.getCustomerByID(1)
        assert customer != None
        assert newCustomer != changedCustomer
        assert customer.id == 1
        assert customer.name == changedCustomer['name']
        assert customer.country == changedCustomer['country']
        assert customer.phone == changedCustomer['phone']
        assert customer.email == changedCustomer['email']


def test_delete(auth,client,app):
    """Tests if API successfully deletes a customer database entry

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
    with app.app_context():    
        newCustomer = { 
            'name':'Test Customer',
            'email': 'test@customer.com',
            'phone':'123456789',
            'country':'PORTUGAL'
        }

        response = client.post("/customers/create",json=newCustomer)
        assert response.status_code == 200

        customer = databaseAPI.getCustomerByID(1)
        assert customer != None

        response = client.post("/customers/delete/1")
        assert response.status_code == 200

        customer = databaseAPI.getCustomerByID(1)
        assert customer == None

