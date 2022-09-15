from flask import render_template, request
from flask_login import current_user
from .. import databaseAPI as DBAPI
from . import utils as Utils
import json

def displayCustomers():
    customers = DBAPI.getCustomer('_ALL_')
    return render_template('customers.html', customers = customers, mode = request.cookies.get('mode'))

def createCustomer(requestData):
    adminAcc = current_user
    # ################# Storage Data ####################    
    name = requestData.get('name')
    email = requestData.get('email')
    phone = requestData.get('phone')
    country = requestData.get('country')
    # ###################################################

    validationR = Utils.validateMultiple_Customer(name, email, phone)
    if not validationR == "":
        return json.dumps({ 'code' : "ERROR", 'message' : "Some of your input fields are incorrect: \n" + str(validationR) })
    
    try:
        DBAPI.createCustomer(name, email, phone, country)
        DBAPI.submitLog(None, adminAcc.id, 'CreatedCustomer', '$$' + str(adminAcc.name) + "$$ has registered the customer '" + str(name) + "'.")
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : 'The database failed to create the customer - #UNKNOWN ERROR' })
    
    return json.dumps({ 'code' : "OKAY" })

def editCustomer(customerid, requestData):
    adminAcc = current_user
    # ################# Storage Data ####################    
    name = requestData.get('name')
    email = requestData.get('email')
    phone = requestData.get('phone')
    country = requestData.get('country')
    # ###################################################

    validationR = Utils.validateMultiple_Customer(name, email, phone)
    if not validationR == "":
        return json.dumps({ 'code' : "ERROR", 'message' : "Incorrect input: \n" + str(validationR) })

    try:
        DBAPI.modifyCustomer(customerid, name, email, phone, country)
        DBAPI.submitLog(None, adminAcc.id, 'EditedCustomer', '$$' + str(adminAcc.name) + "$$ has modified the data of customer '" + str(name) + "'.")
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : 'The database failed to edit the customer data - #UNKNOWN ERROR' })
    
    return json.dumps({ 'code' : "OKAY" })

def deleteCustomer(customerid):
    try:
        DBAPI.deleteCustomer(customerid)
    except Exception:
        return json.dumps({ 'code' : "ERROR", 'message' : 'The database failed to delete the customer - #UNKNOWN ERROR' })

    return json.dumps({ 'code' : "OKAY" })