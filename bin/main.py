from flask import Blueprint, render_template
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/cpanel')
def cpanel():
    return render_template('cpanel.html')

@main.route('/cpanel/product/id/<productid>')
def productDisplay(productid):
    return render_template('product.html', prodID = productid)