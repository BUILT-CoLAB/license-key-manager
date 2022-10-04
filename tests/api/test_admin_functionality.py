import json
import pytest
from bin.models import User
from werkzeug.security import generate_password_hash
from time import time
from bin import database_api, db
import flask_login
from flask import session


@pytest.fixture()
def user_not_owner(app):
    with app.app_context():
        newAdmin = User(email="testing@email.com", password=generate_password_hash(
            "testing"), name="notOwner", timestamp=int(time()), owner=False)
        db.session.add(newAdmin)
        db.session.commit()
        user = User.query.filter_by(id=newAdmin.id).first()
    yield user
    with app.app_context():
        db.session.delete(user)
        db.session.commit()


def test_owner_access_admin_list(auth, client):
    """Tests if API successfully displays admins list

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
    response = client.get("/admins")
    assert response.status_code == 200


def test_non_owner_access_admin_list(auth, client, user_not_owner):
    """Tests if API does not display admins list to non owner as defined in the API documentation

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    user_not_owner : User
        User orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login(username=user_not_owner.name, password="testing")
    with client:
        client.get('/')
        assert session['_user_id'] == str(user_not_owner.id)
        assert flask_login.current_user.name == user_not_owner.name
        response = client.get("/admins")
        assert user_not_owner.owner == False
        assert response.status_code != 200


def test_admin_creation(auth, client, app):
    """Tests if API does not display admins list to non owner as defined in the API documentation

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app : FlaskApp
        The application

    Returns
    -------
    """

    auth.login()
    json_info = {
        'email': 'testing@admin1.com',
        'username': 'admin1',
        'password': 'administrator1'
    }
    response = client.post("/admins/create", json=json_info)
    json_loaded = json.loads(response.data)
    assert response.status_code == 200
    assert json_loaded['code'] == "OKAY"

    with app.app_context():
        user = User.query.filter_by(name=json_info['username']).first()
        assert user != None
        assert user.email == json_info['email']


def test_admin_edit(auth, client, app, user_not_owner):
    """Tests if API successfully edits an admin db entry

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app : FlaskApp
        The application

    user_not_owner : User
        User orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login()
    json_info = {
        'password': "new_testing_password"
    }

    response = client.post(
        "/admins/"+str(user_not_owner.id)+"/edit", json=json_info)
    assert json.loads(response.data)['code'] == "OKAY"
    assert response.status_code == 200

    auth.logout()

    auth.login(username=user_not_owner.name, password="new_testing_password")
    with client:
        client.get('/')
        assert session['_user_id'] == str(user_not_owner.id)
        assert flask_login.current_user.name == user_not_owner.name


def test_admin_toggle_state(client, auth, app, user_not_owner):
    """Tests if API successfully toggles admin account state

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests

    app : FlaskApp
        The application

    user_not_owner : User
        User orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login()

    response = client.post("admins/"+str(user_not_owner.id)+"/togglestatus")
    assert response.status_code == 200
    assert json.loads(response.data)['code'] == "OKAY"

    with app.app_context():
        user = User.query.filter_by(id=user_not_owner.id).first()
        assert user.disabled == True

        response = client.post(
            "admins/"+str(user_not_owner.id)+"/togglestatus")
        assert response.status_code == 200
        assert json.loads(response.data)['code'] == "OKAY"
        user = User.query.filter_by(id=user_not_owner.id).first()
        assert user.disabled == False
