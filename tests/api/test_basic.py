from urllib import response
import pytest
import bin

@pytest.fixture()
def app():
    app = bin.create_app()
    app.config.update({
        "TESTING":True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_login_page(client):
    response = client.get("/")
    assert 200==response.status_code

# Test API redirects when trying to access restricted resources   
def test_unauthorized_access(client):
    response = client.get("/tutorial")
    assert 302==response.status_code
    response = client.get("/products")
    assert 302==response.status_code
    response = client.get("/dashboard")
    assert 302==response.status_code
    response = client.get("/customers")
    assert 302==response.status_code
    response = client.get("/logs/changes")
    assert 302==response.status_code
    response = client.get("/logs/validations")
    assert 302==response.status_code
