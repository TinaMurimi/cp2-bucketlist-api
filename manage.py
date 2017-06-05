# This is the file that is invoked to start up a development server.
# It gets a copy of the app from your package and runs it.
# This won’t be used in production, but it will see a lot of mileage in
# development.

import logging
import os
import re
import sys


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from getpass import getpass
from migrate.versioning import api

from bucketlist.app import app
from bucketlist.app.models import db, User

# Setting a logger in the application and making it print to stdout
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    """Creates the db tables"""

    os.system('createdb bucketlist_test owner postgres')
    os.system('createdb bucketlist owner postgres')

    db.create_all()
    db.session.commit()

    if not os.path.exists(app.config['SQLALCHEMY_MIGRATE_REPO']):
        api.create(app.config['SQLALCHEMY_MIGRATE_REPO'],
                   'database repository')
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    else:
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO'],
            api.version(app.config['SQLALCHEMY_MIGRATE_REPO'])
        )


@manager.command
def dropdb():
    """Drops the db tables"""
    db.drop_all()

    os.system('dropdb bucketlist_test')
    os.system('dropdb bucketlist')


@manager.command
def createadmin():
    """Create admin user"""

    username = input('Enter Admin username: ')
    email = input('Enter Admin email: ')

    users = User.query.filter(User.username.ilike(
        username) | User.email.ilike(email)).first()

    if users:
        raise ValueError('Username or email already exists')

    email_regex = re.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    if not email_regex.match(email):
        raise ValueError('Not a valid email')

    password = getpass()
    assert password == getpass('Password (again):')

    if len(password) < 8 or len(password) > 15:
        raise ValueError('Password should have 8-15 characters')

    try:
        user = User(username=username,
                    email=email,
                    password=password,
                    )

        # User requires to authenticate account before account is activated
        user.active = True
        user.admin = True
        db.session.add(user)
        db.session.commit()

        print('New Admin user registered successfully')

    except Exception as error:
        db.rollback()
        return {'error': str(error)}, 400


if __name__ == '__main__':
    manager.run()
