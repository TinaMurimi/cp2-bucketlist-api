# # This file initializes your application and brings together all of the
# various components

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from flask_restful import Api
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

from ..config import configuration
from .models import db, User, Role

from bucketlist.resources.user_resource import (UserRegistrationAPI,
                                                SingleUserAPI,
                                                UserLoginAPI,
                                                UserLogoutAPI,
                                                )
from bucketlist.resources.bucketlist_resource import (
    BucketlistAPI,
    BucketlistItemAPI,
    SingleBucketlistAPI,
    SingleBucketlistItemAPI,
)

# When instance_relative_config=True if we create our app with the Flask() call
# app.config.from_pyfile() will load the specified file from the
# instance/directory


def ConfigureApp(config_name):
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object(configuration[config_name])

    # Load the configuration from the instance folder: instance/config.py
    # app.config.from_pyfile('config.py', silent=True)

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    # app.config.from_envvar('APP_CONFIG_FILE')
    # app.config.from_object(os.environ['APP_SETTINGS'])
    # $ export APP_CONFIG_FILE=/Users/tinabob/cp2-bucketlist-api/config.py

    # Configure Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    # Configure Compressing
    Compress(app)

    # TO JSON from reordering
    app.config['JSON_SORT_KEY'] = False

    # Bind db to app
    db.init_app(app)

    # Register resources
    api = Api(app)
    api.add_resource(UserRegistrationAPI,
                     '/bucketlist_api/v1.0/auth/register',
                     endpoint='register_user')
    api.add_resource(SingleUserAPI,
                     '/bucketlist_api/v1.0/user/<int:id>',
                     endpoint='single_user')
    api.add_resource(UserLoginAPI,
                     '/bucketlist_api/v1.0/auth/login',
                     endpoint='login')
    api.add_resource(UserLogoutAPI,
                     '/bucketlist_api/v1.0/auth/logout',
                     endpoint='logout')

    api.add_resource(BucketlistAPI,
                     '/bucketlist_api/v1.0/bucketlists',
                     endpoint='bucketlist')
    api.add_resource(SingleBucketlistAPI,
                     '/bucketlist_api/v1.0/bucketlists/<int:id>',
                     endpoint='single_bucketlist')
    api.add_resource(BucketlistItemAPI,
                     '/bucketlist_api/v1.0/bucketlists/<int:id>/items',
                     endpoint='bucketlistitem')
    api.add_resource(SingleBucketlistItemAPI,
                     '/bucketlist_api/v1.0/bucketlists/<int:id>/items/<int:item_id>',
                     endpoint='single_bucketlistitem')

    return app


app = ConfigureApp(config_name="development")
