from itsdangerous import URLSafeTimedSerializer

from bucketlist import app

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])