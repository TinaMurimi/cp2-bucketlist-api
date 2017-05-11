# This is the file that is invoked to start up a development server.
# It gets a copy of the app from your package and runs it.
# This won’t be used in production, but it will see a lot of mileage in
# development.

import os


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# from mom.client import SQLClient
# from Smartfocus.restclient import RESTClient

# from bucketlist.models import db
from bucketlist.models import db
from bucketlist import app

# app.config.from_object("config.testing")
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
