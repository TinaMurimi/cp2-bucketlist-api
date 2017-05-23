import datetime
import jwt
import os

import bucketlist.app

SECRET_KEY = os.environ.get('SECRET_KEY')


def generate_auth_token(issuer, sub):
    """
    Generate a self-contained JSON Web Token to carry all the information necessary within itself.
    A JWT is able to transmit basic information about itself, a payload
            (usually user information), and a signature
    """

    payload = {"iss": issuer,
               "exp": datetime.datetime.utcnow() + datetime.timedelta(
                   days=0, seconds=60 * 60),
               "iat": datetime.datetime.utcnow(),
               "sub": sub,
               }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    ).decode('utf-8')

    return token


def verify_auth_token(token):
    """
    Decodes the authentication token
    """
    try:
        payload = jwt.decode(token,
                             SECRET_KEY)

        if payload:
            return payload["sub"]
        else:
            return 'Forbidden: Please login', 403
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again', 401
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again', 401
