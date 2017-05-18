#!/usr/bin/env python
"""Create a new admin user"""

import sys

from getpass import getpass

from flask import current_app

from . import bcrypt
from .models import db, Role, User, Bucketlist


from flask import current_app
from bull import app, bcrypt
from bull.models import User, db


def main():
    """Main entry point for script."""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if User.query.all():
            print 'A user already exists! Create another? (y/n):',
            create = raw_input()
            if create == 'n':
                return

        print 'Enter Admin user: ',
        username = raw_input()
        
        print 'Enter email address: ',
        email = raw_input()
        
        password = getpass()
        assert password == getpass('Password (again):')

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        print 'User added.'



if __name__ == '__main__':
    sys.exit(main())