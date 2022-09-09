from bin import databaseAPI

def test_creation(auth,client,app):
    """Tests if API successfully creates a product

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
    response = client.get("/products/id/1")
    assert response.status_code == 404
    
    product = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
    }

    response = client.post("/products/create",json=product)
    assert response.status_code == 200

    response = client.get("/products/id/1")
    assert response.status_code == 200
    
    with app.app_context():
        addedProduct = databaseAPI.getProductByID(1)
        assert addedProduct != None
        assert addedProduct.id == 1
        assert addedProduct.name == product['name']
        assert addedProduct.category == product['category']
        assert addedProduct.details == product['details']
        assert addedProduct.image == product['image']


def test_edit(auth,client,app):
    """Tests if API successfully edits a product database entry

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
    response = client.get("/products/id/1")
    assert response.status_code == 404
    
    product = {'name':'Testing product','category': 'CAT 003SA','image':'','details':'this product is for testing purposes only'}
    response = client.post("/products/create",json=product)
    assert response.status_code == 200

    response = client.get("/products/id/1")
    assert response.status_code == 200

    changedProduct = {  'id':1,
                        'name':'Final product',
                        'category': 'CAT 003SAFINAL',
                        'image':'',
                        'details':'this product is the final product'
    }
    response = client.post("/products/edit",json=changedProduct)
    assert response.status_code == 200

    response = client.get("/products/id/1")
    assert response.status_code == 200
    
    with app.app_context():
        addedProduct = databaseAPI.getProductByID(1)
        assert addedProduct != None
        assert addedProduct != product
        assert addedProduct.id == changedProduct['id']
        assert addedProduct.name == changedProduct['name']
        assert addedProduct.category == changedProduct['category']
        assert addedProduct.details == changedProduct['details']
        assert addedProduct.image == changedProduct['image']

    
