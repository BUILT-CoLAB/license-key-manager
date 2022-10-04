from flask import session
import pytest
import flask_login
###########################################################################
# Unauthenticated access
###########################################################################


def test_unauthenticated_views_access(client):
    """Tests if API accepts/rejects unauthenticated access to resource

    Parameters
    ----------
    client : FlaskClient
        The test client to use for requests

    Returns
    -------
    """

    response = client.get("/")
    assert 200 == response.status_code

    response = client.get("/tutorial")
    assert 302 == response.status_code

    response = client.get("/products")
    assert 302 == response.status_code

    response = client.get("/dashboard")
    assert 302 == response.status_code

    response = client.get("/customers")
    assert 302 == response.status_code

    response = client.get("/licenses/1")
    assert 302 == response.status_code

    response = client.get("/logs/changes")
    assert 302 == response.status_code

    response = client.get("/logs/changes/query")
    assert 302 == response.status_code

    response = client.get("/logs/validations")
    assert 302 == response.status_code

    response = client.get("/logs/validations/query")
    assert 302 == response.status_code

    response = client.get("/admins")
    assert 302 == response.status_code

###########################################################################


def test_login(client, auth):
    """Tests API login feature with defined standard username/password

    Parameters
    ----------
    client : FlaskClient
        The test client to use for requests

    auth : AuthActions
        AuthActions class object to use for login

    Returns
    -------
    """

    response = auth.login()
    assert response.data == b'OK'
    assert response.status_code == 200

    with client:
        client.get('/')
        assert session['_user_id'] == '1'
        assert flask_login.current_user.name == 'root'

###########################################################################


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'The account does not exist or the login data is incorrect.'),
    ('test', 'a', b'The account does not exist or the login data is incorrect.'),
    ('test', 'test', b'The account has been disabled.')
))
def test_login_validate_input(auth, username, password, message):
    """Tests API login feature with defined parameters

    Parameters
    ----------    
    auth : AuthActions
        AuthActions class object to use for login

    username : str
        The username string

    password : str
        The password string

    message : str
        The message to compare with the request received data

    Returns
    -------
    """

    response = auth.login(username, password)
    assert message in response.data

###########################################################################


def test_logout(client, auth):
    """Tests API logout feature

    Parameters
    ----------    
    client : FlaskClient
        The test client to use for requests

    auth : AuthActions
        AuthActions class object to use for login

    Returns
    -------
    """

    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

###########################################################################


def test_authenticated_views_access(auth, client):
    """Tests if API accepts/rejects authenticated access to resource

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    Returns
    -------
    """

    auth.login()
    response = client.get("/")
    assert 200 == response.status_code
    response = client.get("/tutorial")
    assert 200 == response.status_code
    response = client.get("/products")
    assert 200 == response.status_code
    response = client.get("/dashboard")
    assert 200 == response.status_code
    response = client.get("/customers")
    assert 200 == response.status_code
    response = client.get("/licenses/1")
    assert 404 == response.status_code
    response = client.get("/logs/changes")
    assert 200 == response.status_code
    response = client.get("/logs/changes/query", query_string={})
    assert 500 == response.status_code
    response = client.get(
        "/logs/changes/query", query_string={'adminid': -1, 'datestart': -1, 'dateend': -1})
    assert 200 == response.status_code
    response = client.get("/logs/validations")
    assert 200 == response.status_code
    response = client.get("/logs/validations/query", query_string={})
    assert 500 == response.status_code
    response = client.get("/logs/validations/query",
                          query_string={'typeSearch': '', 'datestart': -1, 'dateend': -1})
    assert 200 == response.status_code
    response = client.get("/admins")
    assert 200 == response.status_code
