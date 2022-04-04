from . import db

# Declare the User Model for the Database (Admin, mostly)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    privateK = db.Column(db.String(100), unique=True)
    publicK = db.Column(db.String(100), unique=True)
    apiK = db.Column(db.String(100), unique=True)