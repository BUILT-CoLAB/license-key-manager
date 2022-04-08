from flask import Blueprint, render_template, request
from sqlalchemy import text

from . import db

main = Blueprint('main', __name__)

#
# sql = text('SELECT * FROM product')
# result = db.engine.execute(sql)
#

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

###########################################################################

@main.route('/cpanel')
def cpanel():
    getProduct("hey")
    return render_template('cpanel.html')

@main.route('/cpanel/product/create', methods=['POST'])
def createProduct():
    dataInfo = request.get_json()
    print(dataInfo)
    sql = text("INSERT into product (name, logo, privateK, publicK, apiK) VALUES ('dasda', 'asdasda', 'asdasda', 'asdasda', 'asdasda')")
    result = db.engine.execute(sql)
    return "XD"

###########################################################################

@main.route('/cpanel/product/id/<productid>')
def productDisplay(productid):
    return render_template('product.html', prodID = productid)

@main.route('/cpanel/product/id/<productid>/createkey')
def createKey(productid):
    return render_template('product.html', prodID = productid)

def getProduct(searchString):
    sql = text('select name from product')
    result = db.engine.execute(sql)
    names = [row[0] for row in result]
    print(names)
