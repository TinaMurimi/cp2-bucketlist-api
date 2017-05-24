# These are the models for the application

import jwt

from datetime import date, datetime
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_sqlalchemy import Model, SQLAlchemy

from sqlalchemy import DateTime, Column


class TimestampedModel(Model):
    created_on = Column(DateTime,
                        nullable=False,
                        default=datetime.now().isoformat(
                            sep=' ',
                            timespec='minutes'))


db = SQLAlchemy(model_class=TimestampedModel)

auth = HTTPBasicAuth()
bcrypt = Bcrypt()


class User(db.Model):

    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    bucketlist = db.relationship(
        'Bucketlist', backref=db.backref('user', uselist=False),
        lazy='immediate', order_by='Bucketlist.list_id')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password.encode('utf8'), 12).decode('utf8')
        self.authenticated = False
        self.active = False

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_id(self):
        """Return username to satisfy Flask-Login's requirements"""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return self.authenticated

    def is_active(self):
        """Return if user has activated their account"""
        return self.active

    def is_anonymous(self):
        """False, as anonymous users aren't supported"""
        return False

    @auth.verify_password
    def verify_password(self, password):
        if bcrypt.check_password_hash(self.password, password):
            return True

        return False


class Bucketlist(db.Model):

    __tablename__ = 'Bucketlist'

    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)

    date_modified = db.Column(db.DateTime,
                              default=datetime.now().isoformat(
                                  sep=' ',
                                  timespec='minutes'))

    created_by = db.Column(db.Integer, db.ForeignKey(
        'User.user_id'), nullable=False)

    items = db.relationship(
        'Bucketlist_Item', backref=db.backref('bucketlist', uselist=False),
        lazy='immediate', order_by='Bucketlist_Item.item_id')

    def __init__(self, list_name, description, created_by):
        self.list_name = list_name
        self.description = description
        self.created_by = created_by
        self.is_completed = False
        self.date_modified = datetime.now().isoformat(
            sep=' ',
            timespec='minutes')

    def __repr__(self):
        """Return Bucketlist name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist id"""
        return self.list_id

    def list_is_completed(self):
        """Return True if the all bucketlist items have been completed"""
        return self.is_completed


class Bucketlist_Item(db.Model):

    __tablename__ = 'Bucketlist_Item'

    item_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'Bucketlist.list_id'), nullable=False)
    item_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)

    date_modified = db.Column(db.DateTime,
                              default=datetime.now().isoformat(
                                  sep=' ',
                                  timespec='minutes'))

    def __init__(self, item_name, description, list_id):
        self.item_name = item_name
        self.list_id = list_id
        self.description = description
        self.is_completed = False
        self.date_modified = datetime.now().isoformat(
            sep=' ',
            timespec='minutes')

    def __repr__(self):
        """Return Bucketlist item name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist item id"""
        return self.item_id

    def list_is_completed(self):
        """Return True if item has been completed"""
        return self.is_completed
