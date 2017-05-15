# # This file initializes your application and brings together all of the
# various components

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

from termcolor import colored

from bucketlist.config import configuration
# from bucketlist.models import User, Role
import bucketlist.models

# When instance_relative_config=True if we create our app with the Flask() call
# app.config.from_pyfile() will load the specified file from the
# instance/directory

app = Flask(__name__, instance_relative_config=True)
# db = SQLAlchemy(app)


def ConfigureEnv(config_name):
    # Load the default configuration
    app.config.from_object(configuration[config_name])

ConfigureEnv(config_name="default")

# Check if DB url is specified
if app.config['SQLALCHEMY_DATABASE_URI'] is None:
    print ("\nNeed database config\n")
    sys.exit(1)
else:
    print (colored("\nDatabase used:--->", "cyan"), app.config['SQLALCHEMY_DATABASE_URI'], "\n")

# Load the configuration from the instance folder: instance/config.py
# app.config.from_pyfile('config.py', silent=True)

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
# app.config.from_envvar('APP_CONFIG_FILE')
# app.config.from_object(os.environ['APP_SETTINGS'])
# $ export APP_CONFIG_FILE=/Users/tinabob/cp2-bucketlist-api/config.py

# Configure Security
user_datastore = SQLAlchemyUserDatastore(models.db, models.User, models.Role)

# Configure Compressing
Compress(app)

# Create an instance of Bcyrpt
bcyrpt = Bcrypt(app)

# Flask login
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.init_app(app)

# View to be used for login
login_manager.login_view = "login"

# Flask-WTF csrf protection
csrf = CSRFProtect()
csrf.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()
