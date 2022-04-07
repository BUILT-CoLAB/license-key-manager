from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import login_user
from .models import User
from werkzeug.security import check_password_hash

from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    #user = db.get_user(email) 
    user = User.query.filter_by(email=email).first()


    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))
    
    # Login process
    #dataInfo = request.get_json()
    #print(dataInfo)
    #return 'Login XD'

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    #if not user or not check_password_hash(user.password, password):
    #    flash('Please check your login details and try again.')
    #    return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    # login_user(user, remember=remember)
    # 

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    return 'Logout'