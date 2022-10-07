from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from os.path import exists

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
_KEY_LENGTH_ = 64


def create_app(testing=None, database="database/sqlite.db"):

    load_dotenv()

    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv(
        "SECRET_KEY") or 'secret-key-goes-here'
    if(testing is None or testing is False):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + database
    else:
        # in-memory db for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.index'
    login_manager.init_app(app)

    from .models import User  # pylint: disable=C0415
    from .auth import auth as auth_blueprint  # pylint: disable=C0415
    from .main import main as main_blueprint  # pylint: disable=C0415

    @ login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    with app.app_context():

        if(not exists(app.config['SQLALCHEMY_DATABASE_URI'])):
            from . import database_api as DBAPI  # pylint: disable=C0415
            db.create_all(app=app)
        DBAPI.generateUser(os.getenv("ADMINUSERNAME"), os.getenv(
            "ADMINPASSWORD"), os.getenv("ADMINEMAIL"))

    return app
