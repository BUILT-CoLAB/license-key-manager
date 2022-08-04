from flask import Blueprint, render_template, request
from flask_httpauth import HTTPTokenAuth
from flask_login import login_required
from . import databaseAPI as DBAPI
import json
import time
import math

from .handlers import admins as AdminHandler, customers as CustomerHandler, logs as LogHandler, products as ProductHandler, licenses as LicenseHandler, validation as ValidationHandler

main = Blueprint('main', __name__)
auth = HTTPTokenAuth(scheme='Bearer')


@main.route('/')
def index():
    return render_template('index.html', mode=request.cookies.get('mode'))


@main.route('/healthcheck')
def health():
    return


@main.route('/tutorial')
@login_required
def tutorial():
    return render_template('tutorial.html', mode=request.cookies.get('mode'))


@main.route('/dashboard')
@login_required
def cpanel():
    activated, awaitingApproval = DBAPI.getKeyStatistics()
    successfulV, unsuccessfulV = DBAPI.queryValidationsStats()
    if(activated == 0 and awaitingApproval == 0):
        ratio = 100
    else:
        ratio = (activated / (activated + awaitingApproval)) * 100
    return render_template('cpanel.html', products=DBAPI.getProductCount(), activated=activated, awaitingApproval=awaitingApproval, ratio=round(ratio), mode=request.cookies.get('mode'), successV=successfulV, unsuccessV=unsuccessfulV)


###########################################################################
# PRODUCT HANDLING
###########################################################################
@main.route('/products')
@login_required
def products():
    return ProductHandler.displayProductList()


@main.route('/products/id/<productid>')
@login_required
def productDisplay(productid):
    return ProductHandler.displayProduct(productid)


@main.route('/products/create', methods=['POST'])
@login_required
def createProduct():
    return ProductHandler.createProduct(request.get_json())


@main.route('/products/edit', methods=['POST'])
@login_required
def editProduct():
    return ProductHandler.editProduct(request.get_json())


@main.route('/clearcheck/<productid>')
@login_required
def clearProductCheck(productid):
    # DEBUG ROUTE - No need to remove as it doesn't affect the state of the application.
    DBAPI.resetProductCheck(productid)
    return "DONE! Next time the product page of the indicated product is loaded, the server will check for expired keys."


###########################################################################
# CUSTOMER HANDLING
###########################################################################
@main.route('/customers')
@login_required
def customers():
    return CustomerHandler.displayCustomers()


@main.route('/customers/create', methods=['POST'])
@login_required
def createCustomer():
    return CustomerHandler.createCustomer(request.get_json())


@main.route('/customers/edit/<customerid>', methods=['POST'])
@login_required
def modifyCustomer(customerid):
    return CustomerHandler.editCustomer(customerid, request.get_json())


@main.route('/customers/delete/<customerid>', methods=['POST'])
@login_required
def deleteCustomer(customerid):
    return CustomerHandler.deleteCustomer(customerid)


###########################################################################
# LICENSE KEY HANDLING
###########################################################################
@main.route('/product/<productid>/createlicense', methods=['POST'])
@login_required
def createLicense(productid):
    return LicenseHandler.createLicense(productid, request.get_json())


@main.route('/licenses/<licenseid>')
@login_required
def licenseDisplay(licenseid):
    return LicenseHandler.displayLicense(licenseid)


@main.route('/licenses/editkeys', methods=['POST'])
@login_required
def updateKeyState():
    return LicenseHandler.changeLicenseState(request.get_json())


@main.route('/licenses/<keyid>/removedevice', methods=['POST'])
@login_required
def hardwareIDRemove(keyid):
    return LicenseHandler.unlinkHardwareDevice(keyid, request.get_json().get('hardwareID'))


###########################################################################
# CHANGELOG HANDLING
###########################################################################
@main.route('/logs/changes')
@login_required
def changelogs():
    return LogHandler.displayChangelog()


@main.route('/logs/changes/query')
@login_required
def getchangelog():
    return LogHandler.queryLogs(request.args.to_dict())


###########################################################################
# VALIDATION LOG HANDLING
###########################################################################
@main.route('/logs/validations')
@login_required
def validationlogs():
    return LogHandler.displayValidationLog()


@main.route('/logs/validations/query')
@login_required
def getvalidationlogs():
    return LogHandler.queryValidationLogs(request.args.to_dict())


###########################################################################
# ADMINISTRATOR ACCOUNTS - HANDLING
###########################################################################
@main.route('/admins')
@login_required
def adminsDisplay():
    return AdminHandler.displayAdminPage()


@main.route('/admins/create', methods=['POST'])
@login_required
def adminCreate():
    return AdminHandler.createAdmin(request.get_json())


@main.route('/admins/<userid>/edit', methods=['POST'])
@login_required
def adminEdit(userid):
    return AdminHandler.editAdmin(userid, request.get_json())


@main.route('/admins/<userid>/togglestatus', methods=['POST'])
@login_required
def adminToggleStatus(userid):
    return AdminHandler.toggleAdminStatus(userid)


###########################################################################
# VALIDATION PROCESS
###########################################################################
@main.route('/api/v1/validate', methods=['POST'])
def validate_product():
    return ValidationHandler.handleValidation(request.get_json())
