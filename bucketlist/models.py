# This is where you define the models of your application.
# This may be split into several modules in the same way as views.py

# datetime.fromtimestamp(time.time())
from datetime import date

from flask_sqlalchemy import SQLAlchemy

# from bucketlist import db

db = SQLAlchemy()

roles_users = db.Table(
    'roles_user',
    db.Column('user_id', db.Integer(), db.ForeignKey('User.user_id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('Role.role_id'))
)


class Role(db.Model):

    __tablename__ = 'Role'

    role_id = db.Column(db.Integer(), primary_key=True)
    role_name = db.Column(db.String(20), unique=True)
    description = db.Column(db.String(50))

    def __init__(self, role_name):
        self.role_name = role_name

    def __repr__(self):
        return '<Role %r>' % (self.role_name)


class User(db.Model):

    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    roles = db.Column(db.String(5), nullable=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())

    def __init__(self, username, email, password, roles):
        self.username = username
        self.email = email
        self.password = password
        self.authenticated = authenticated
        self.active = active
        self.roles = roles

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


class Bucketlist(db.Model):

    __tablename__ = 'Bucketlist'

    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(20), unique=True, nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())
    date_modified = db.Column(db.DateTime, default=date.today().isoformat())
    created_by = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    def __init__(self, list_name, created_by):
        self.list_name = list_name
        self.created_by = created_by

        self.is_completed = False
        self.created_on = date.today().isoformat()
        self.date_modified = date.today().isoformat()

    def __repr__(self):
        """Return Bucketlist name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist id"""
        return self.list_id

    def list_is_completed(self):
        """Return True if the all bucketlist items have been completed"""
        return self.is_completed


class list_Item(db.Model):

    __tablename__ = 'list_Item'

    item_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('Bucketlist.list_id'))
    item_name = db.Column(db.String(20), unique=True, nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime, default=date.today().isoformat())
    date_modified = db.Column(db.DateTime, default=date.today().isoformat())

    def __init__(self, item_name, list_id):
        self.item_name = item_name
        self.list_id = list_id

        self.is_completed = False
        self.created_on = date.today().isoformat()
        self.date_modified = date.today().isoformat()

    def __repr__(self):
        """Return Bucketlist item name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist item id"""
        return self.item_id

    def list_is_completed(self):
        """Return True if item has been completed"""
        return self.is_completed
