# This file contains most of the configuration variables that the app needs

import logging
import os

from flask import Flask
from flask_compress import Compress

# from .models import User, Bucketlist

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config(object):
    DEBUG = False
    TESTING = False

    # Configuration for the Flask-Bcrypt extension to hash user passwords
    BCRYPT_LEVEL = 12

    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    # export DATABASE_URL="postgresql://postgres@localhost/bucketlist"

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/bucketlist'
    # Sdds significant overhead and will be disabled by default in the future
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # True: SQLAlchemy will log all the statements issued to stderr
    SQLALCHEMY_ECHO = False

    # Where to store the SQLAlchemy-migrate data files
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')

    SECRET_KEY = 'hsfjdkw930qeddncsmd93847fuwie2903fh3039f3'

    RESULTS_PER_PAGE = 20
    JSON_SORT_KEYS = False


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/bucketlist_test'
    TESTING = True
    SECRET_KEY = os.environ.get('SECRET_KEY')


configuration = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    "testing": TestingConfig,
}
