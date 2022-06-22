from pickle import TRUE
from flask_login import UserMixin
from flask import url_for
from . import db

# Declare the User Model for the Database (Admin, mostly)
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column( db.Integer, primary_key=True )
    email = db.Column( db.String(100), unique=True )
    password = db.Column( db.String(150) )
    name = db.Column( db.String(100), unique=True )
    owner = db.Column( db.Boolean, default = False )
    disabled = db.Column( db.Boolean, default = False )
    timestamp = db.Column( db.Integer, nullable = False )
    changelogs = db.relationship('Changelog', cascade='all,delete', backref='user')

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column( db.Integer, primary_key=True )
    name = db.Column( db.String(100), unique=True )
    category = db.Column( db.String(100) )
    image = db.Column( db.String(150) , nullable=False )
    details = db.Column( db.String(1000) )
    privateK = db.Column(db.String(1100), unique=True)
    publicK = db.Column(db.String(1100), unique=True)
    apiK = db.Column( db.String(100), unique=True )
    keys = db.relationship('Key', cascade='all,delete', backref='product')

class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column( db.String(100) )
    email = db.Column( db.String(100), unique = True)
    phone = db.Column( db.String(20) )
    country = db.Column( db.String(50) )
    registrydate = db.Column( db.Integer, nullable=False)
    keys = db.relationship('Key', cascade='all,delete', backref='client')

class Key(db.Model):
    __tablename__ = "key"
    id = db.Column(db.Integer, primary_key=True)
    productid = db.Column(db.Integer, db.ForeignKey('product.id', ondelete="cascade"), nullable=False)
    clientid = db.Column(db.Integer, db.ForeignKey('client.id', ondelete="cascade"), nullable=False)
    serialkey = db.Column( db.String(100), unique = True)
    maxdevices = db.Column( db.Integer )
    devices = db.Column( db.Integer )
    status = db.Column( db.Integer )
    expirydate = db.Column( db.Integer, nullable=False)
    registrations = db.relationship('Registration', cascade='all,delete', backref='key')
    changelogs = db.relationship('Changelog', cascade='all,delete', backref='key')

class Registration(db.Model):
    __tablename__ = "registration"
    id = db.Column(db.Integer, primary_key=True)
    keyID = db.Column(db.Integer, db.ForeignKey('key.id', ondelete="cascade"), nullable=False)
    hardwareID = db.Column(db.String(200), nullable=False)

class Changelog(db.Model):
    __tablename__ = "changeLog"
    id = db.Column( db.Integer, primary_key=True )
    keyID = db.Column( db.Integer, db.ForeignKey('key.id', ondelete="cascade"), nullable=True )
    userid = db.Column( db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True )
    timestamp = db.Column( db.Integer, nullable=False )
    action = db.Column( db.String(25) )
    description = db.Column( db.String(150), nullable=False, default='' )
