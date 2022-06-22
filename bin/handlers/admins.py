from flask import Blueprint, render_template, request
from .. import databaseAPI as DBAPI

def displayAdminPage():
    userList = DBAPI.obtainUser('_ALL_')
    return render_template('users.html', users = userList, mode = request.cookies.get('mode'))

def createAdmin(requestData):
    DBAPI.createUser(requestData.get('email'), requestData.get('username'), requestData.get('password'))
    return "SUCCESS"

def editAdmin(adminID, requestData):
    DBAPI.changeUserPassword( adminID, requestData.get('password') )
    return "SUCCESS"

def toggleAdminStatus(adminID):
    DBAPI.toggleUserStatus(adminID)
    return "SUCCESS"