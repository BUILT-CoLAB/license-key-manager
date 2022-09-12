from bin import databaseAPI
import pytest

from bin.keys import create_product_keys
from bin.models import Product
from bin import db 

@pytest.fixture
def created_product(app):
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
    
    product = { 'name':'Testing product',
                'category': 'CAT 003SA',
                'image':'',
                'details':'this product is for testing purposes only'
    }

    response = client.post("/products/create",json=product)
    assert response.status_code == 200
    
    with app.app_context():
        addedProduct = databaseAPI.getProductByID(1)
        assert addedProduct != None
        assert addedProduct.id == 1
        assert addedProduct.name == product['name']
        assert addedProduct.category == product['category']
        assert addedProduct.details == product['details']
        assert addedProduct.image == product['image']


def test_access(auth,client,app,created_product):
    """Tests if API successfully lists a product info when the product exists

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests
    
    app :  FlaskApp
        The app needed to query the Database

    created_product : Product
        Product orm object added to the database before the test (fixture)

    Returns
    -------
    """

    auth.login()

    # Tries to list an existent product
    response = client.get("/products/id/"+str(created_product.id))
    assert response.status_code == 200

    # Tries to list an unexistent product
    response = client.get("/products/id/"+str(created_product.id+1))
    assert response.status_code == 404


def test_edit(auth,client,app,created_product):
    """Tests if API successfully edits a product database entry

    Parameters
    ----------
    auth : AuthActions
        AuthActions class object to use for login

    client : FlaskClient
        The test client to use for requests
    
    app :  FlaskApp
        The app needed to query the Database

    created_product : Product
        Product orm object added to the database before the test (fixture)
        
    Returns
    -------
    """

    auth.login()

    unexistent_product = { 
        'id':created_product.id+1,
        'name':'Final product',
        'category': 'CAT 003SAFINAL',
        'image':'',
        'details':'this product is the final product'
    }

    # Tries to edit an unexistent product
    response = client.post("/products/edit",json=unexistent_product)
    # RESPONSE STATUS CODE SHOULD NOT BE 200.
    # THE SERVER SENDS 200 BECAUSE JSON.DUMPS DOES NOT THINK AN ERROR OCURRED
    # THAT NEEDS TO BE CHANGED. THROW EXCEPTION OR SEND AN DIFFERENT HTTP CODE
    assert response.status_code != 200
    assert response.status_code != 500

    changedProduct = {  
        'id':created_product.id,
        'name':'Final product',
        'category': 'CAT 003SAFINAL',
        'image':'',
        'details':'this product is the final product'
    }

    # Tries to edit an existent product
    response = client.post("/products/edit",json=changedProduct)
    assert response.status_code == 200

    with app.app_context():
        addedProduct = databaseAPI.getProductByID(1)
        assert addedProduct != None
        assert addedProduct != created_product
        assert addedProduct.id == changedProduct['id']
        assert addedProduct.name == changedProduct['name']
        assert addedProduct.category == changedProduct['category']
        assert addedProduct.details == changedProduct['details']
        assert addedProduct.image == changedProduct['image']

    
