from pickle import TRUE
from flask_login import UserMixin
from . import db

# Declare the User Model for the Database (Admin, mostly)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

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
    serialkey = db.Column( db.String(100) )
    maxdevices = db.Column( db.Integer )
    devices = db.Column( db.Integer )

class Devices(db.Model):
    __tablename__ = "devices"
    licensekey = db.Column(db.String(150),primary_key = True)
    hardwareID = db.Column(db.String(150),primary_key = True)