# This is the file that is invoked to start up a development server.
# It gets a copy of the app from your package and runs it.
# This won’t be used in production, but it will see a lot of mileage in
# development.

import os

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restful import Api

from termcolor import colored

from bucketlist.app import app
from bucketlist.app.models import db
from bucketlist.resources.user_resource import UserRegistrationAPI, SingleUserAPI


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# api = Api(app)
# api.add_resource(UserRegistrationAPI,
#                  '/bucketlist_api/v1.0/auth/user', endpoint='register_user')
# api.add_resource(SingleUserAPI,
#                  '/bucketlist_api/v1.0/auth/user/<int:id>', endpoint='single_user')

# Check if DB url is specified
if app.config['SQLALCHEMY_DATABASE_URI'] is None:
    print ("\nNeed database config\n")
    sys.exit(1)
else:
    print (colored("\nDatabase used:--->", "cyan"),
           app.config['SQLALCHEMY_DATABASE_URI'], "\n")
    # print (colored("\nSecret Key:--->", "magenta"), app.config['SECRET_KEY'], "\n")

if __name__ == '__main__':
    manager.run()
