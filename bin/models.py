from pickle import TRUE
from flask_login import UserMixin
from . import db

# Declare the User Model for the Database (Admin, mostly)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(100), unique=True)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column( db.Integer, primary_key=True )
    name = db.Column( db.String(100), unique=True )
    logo = db.Column( db.String(150) )
    privateK = db.Column(db.String(1100), unique=True)
    publicK = db.Column(db.String(1100), unique=True)
    apiK = db.Column( db.String(100), unique=True )

class Key(db.Model):
    __tablename__ = "key"
    id = db.Column(db.Integer, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customername = db.Column( db.String(100) )
    customeremail = db.Column( db.String(100) )
    customerphone = db.Column( db.String(20) )
    serialkey = db.Column( db.String(100), unique = True)
    maxdevices = db.Column( db.Integer )
    devices = db.Column( db.Integer )
    status = db.Column( db.Integer )
    expirydate = db.Column( db.Integer, nullable=False)

class Registration(db.Model):
    __tablename__ = "registration"
    id = db.Column(db.Integer, primary_key=True)
    keyID = db.Column(db.Integer, db.ForeignKey('key.id'), nullable=False)
    hardwareID = db.Column(db.String(200), nullable=False)
    
class Changelog(db.Model):
    __tablename__ = "changeLog"
    id = db.Column(db.Integer, primary_key=True)
    keyID = db.Column(db.Integer, db.ForeignKey('key.id'), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(25))
