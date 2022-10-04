from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from . import database_api as DBAPI

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Obtain form data
    data_info = request.get_json()

    username = data_info.get('emailData')
    passwordData = data_info.get('passwordData')

    user_object = DBAPI.obtainUser(username)

    if not user_object or not check_password_hash(user_object.password, passwordData):
        return "The account does not exist or the login data is incorrect."

    if user_object.disabled is True:
        return "The account has been disabled."

    login_user(user_object)
    return "OK"


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


def getCurrentUser():
    return current_user
