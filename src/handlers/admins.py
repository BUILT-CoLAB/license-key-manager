from flask import render_template, request
from flask_login import current_user as adminAcc
from .. import database_api as DBAPI
from . import utils as Utils
import json


def displayAdminPage():
    if(not adminAcc.owner):
        return 'Unauthorized access', 401
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('users.html', users=userList, mode=request.cookies.get('mode'))


def createAdmin(requestData):
    if(not adminAcc.owner):
        return 'Unauthorized access', 401
    email = requestData.get('email')
    username = requestData.get('username')
    password = requestData.get('password')
    validationR = Utils.validateMultiple_Admin(username, password, email)
    if not validationR == "":
        return json.dumps({'code': "ERROR", 'message': "Some of your input fields are incorrect: \n" + str(validationR)})
    try:
        DBAPI.createUser(requestData.get('email'), requestData.get(
            'username'), requestData.get('password'))
    except Exception:
        return json.dumps({'code': "ERROR", 'message': 'The database failed to create the admin account - #UNKNOWN ERROR'})

    return json.dumps({'code': "OKAY"})


def editAdmin(adminID, requestData):
    if(not adminAcc.owner):
        return 'Unauthorized access', 401
    password = requestData.get('password')
    try:
        Utils.validatePassword(password)
    except Exception:
        return json.dumps({'code': "ERROR", 'message': "Some of your input fields are incorrect: \n- Invalid Password"})
    try:
        DBAPI.changeUserPassword(adminID, requestData.get('password'))
    except Exception:
        return json.dumps({'code': "ERROR", 'message': 'The database failed to edit the password of the account - #UNKNOWN ERROR'})
    return json.dumps({'code': "OKAY"})


def toggleAdminStatus(adminID):
    if(not adminAcc.owner):
        return 'Unauthorized access', 401
    try:
        DBAPI.toggleUserStatus(adminID)
    except Exception:
        return json.dumps({'code': "ERROR", 'message': 'The database failed to disable/enable the account - #UNKNOWN ERROR'})
    return json.dumps({'code': "OKAY"})
