import os

from flask import Flask, render_template
from flask_login import login_required, current_user

from .extensions import login_manager, csrf
from .models import db, Role, User, Bucketlist
from .util import ts, send_email

from bucketlist.config import configure_app


app = Flask(__name__, instance_relative_config=True)
app = configure_app(app)


