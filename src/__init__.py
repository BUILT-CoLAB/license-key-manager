from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from os.path import exists
from . import database_api as DBAPI
from .models import User
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
_KEY_LENGTH_ = 64


def create_app(testing=None, database=None):

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    if(testing is None or testing is False):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/sqlite.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+database
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.index'
    login_manager.init_app(app)

    @ login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    with app.app_context():

        load_dotenv()
        if(not exists('sqlite.db')):
            db.create_all(app=app)
        DBAPI.generateUser(os.getenv("ADMINUSERNAME"), os.getenv(
            "ADMINPASSWORD"), os.getenv("ADMINEMAIL"))

    return app
