import os
import tempfile

import pytest
from bin import create_app, databaseAPI


@pytest.fixture
def app():
    db_fd,db_path = tempfile.mkstemp()
    app = create_app(testing=True,database=db_path)
    
    with app.app_context():                
        databaseAPI.generateUser("test","test", "test@test.com")    
        user = databaseAPI.obtainUser("test")
        databaseAPI.toggleUserStatus(user.id)
        
        

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """PyTest fixture to return FlaskClient to be used by test functions

    Parameters
    ----------    
    app : FlaskApp
        The base FlaskApp

    Returns
    -------
    client: FlaskClient
        FlaskClient to be used by test functions
        
    """

    return app.test_client()


@pytest.fixture
def runner(app):
    """PyTest fixture to return FlaskClient to be used by test functions

    Parameters
    ----------    
    app : FlaskApp
        The base FlaskApp

    Returns
    -------
    cliRunner: FlaskCliRunner
        FlaskCliRunner to be used by test functions
        
    """

    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='root', password='root'):
        return self._client.post(
            '/login',
            json={'emailData': username, 'passwordData': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)