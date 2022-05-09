from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from . import db
from . import databaseAPI as DBAPI

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Obtain form data
    dataInfo = request.get_json()

    username = dataInfo.get('emailData')
    passwordData = dataInfo.get('passwordData')

    userObject = DBAPI.obtainUser(username)

    if not userObject or not check_password_hash(userObject.password, passwordData):
        return "The account does not exist or the login data is incorrect."

    login_user(userObject)
    return "OK"

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))