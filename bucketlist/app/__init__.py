# # This file initializes your application and brings together all of the
# various components

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from flask_restful import Api
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

from bucketlist.config import configuration
from bucketlist.app.models import db, User

from bucketlist.resources.user_resource import (UserRegistrationAPI,
                                                AllRegisteredUsers,
                                                SingleUserAPI,
                                                UserLoginAPI,
                                                )
from bucketlist.resources.bucketlist_resource import (
    BucketlistAPI,
    BucketlistItemAPI,
    SingleBucketlistAPI,
    SingleBucketlistItemAPI,
)


def ConfigureApp(config_name):
    if config_name is None:
        config_name = ("staging")

    # When instance_relative_config=True if we create our app with the Flask()
    # call app.config.from_pyfile() will load the specified file from the
    # instance/directory
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

    # Configure Compressing
    Compress(app)

    # TO JSON from reordering
    app.config['JSON_SORT_KEYS'] = False

    # Bind db to app
    db.init_app(app)

    # Register resources
    api = Api(app)
    api.add_resource(UserRegistrationAPI,
                     '/bucketlist_api/v1.0/auth/register',
                     endpoint='register_user')
    api.add_resource(AllRegisteredUsers,
                     '/bucketlist_api/v1.0/users',
                     endpoint='all_users')
    api.add_resource(SingleUserAPI,
                     '/bucketlist_api/v1.0/user/<int:id>',
                     endpoint='single_user')
    api.add_resource(UserLoginAPI,
                     '/bucketlist_api/v1.0/auth/login',
                     endpoint='login')

    api.add_resource(BucketlistAPI,
                     '/bucketlist_api/v1.0/bucketlists',
                     endpoint='bucketlist')
    api.add_resource(SingleBucketlistAPI,
                     '/bucketlist_api/v1.0/bucketlists/<int:id>',
                     endpoint='single_bucketlist')
    api.add_resource(BucketlistItemAPI,
                     '/bucketlist_api/v1.0/bucketlists/<int:id>/items',
                     endpoint='bucketlistitem')
    api.add_resource(
        SingleBucketlistItemAPI,
        '/bucketlist_api/v1.0/bucketlists/<int:id>/items/<int:item_id>',
        endpoint='single_bucketlistitem')

    return app


config_name = os.getenv('APP_SETTINGS')
app = ConfigureApp(config_name=config_name)
