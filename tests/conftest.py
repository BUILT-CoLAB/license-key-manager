import os
import tempfile

import pytest
from bin import create_app,db, databaseAPI


@pytest.fixture
def app():
    db_fd,db_path = tempfile.mkstemp()
    app = create_app(testing=True,database=db_path[1])
    
    
    
    with app.app_context():                
        user = databaseAPI.obtainUser("test")
        if(user is None):
            databaseAPI.generateUser("test","test", "test@test.com")    
            user = databaseAPI.obtainUser("test")
            databaseAPI.toggleUserStatus(user.id)    
        

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
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