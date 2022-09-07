from flask import session,g
import pytest
import flask_login
###########################################################################
################### Unauthenticated access
###########################################################################

################### Authorized access
def test_login_page(client):
    response = client.get("/")
    assert 200==response.status_code

################### Unauthorized access
def test_tutorial(client):
    response = client.get("/tutorial")
    assert 302==response.status_code

def test_products(client):
    response = client.get("/products")
    assert 302==response.status_code

def test_dashboard(client): 
    response = client.get("/dashboard")
    assert 302==response.status_code

def test_customers(client): 
    response = client.get("/customers")
    assert 302==response.status_code

def test_logs_changes(client): 
    response = client.get("/logs/changes")
    assert 302==response.status_code

def test_logs_validation(client): 
    response = client.get("/logs/validations")
    assert 302==response.status_code

###########################################################################
################### Authenticated access
###########################################################################

################### Authorized Access

def test_login(client, auth):
    response = auth.login()
    assert response.data == b'OK'
    assert response.status_code == 200

    with client:
        client.get('/')
        assert session['_user_id'] == '1'
        assert flask_login.current_user.name == 'root'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'The account does not exist or the login data is incorrect.'),
    ('test', 'a', b'The account does not exist or the login data is incorrect.'),
    ('test', 'test', b'The account has been disabled.')
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

