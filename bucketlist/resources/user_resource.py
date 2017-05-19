import datetime
import jwt
import re

from flask import Flask, g, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from functools import wraps

from bucketlist.resources.views import generate_auth_token, verify_auth_token
from bucketlist.app.models import db, User, Bucketlist, Bucketlist_Item

user_fields = {
    'user_id':  fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
}


class UserRegistrationAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str,
                                   help='No username provided')
        self.reqparse.add_argument(
            "email", type=str, help='No email provided')
        self.reqparse.add_argument(
            "password", type=str)

        super(UserRegistrationAPI, self).__init__()

    def post(self):

        args = self.reqparse.parse_args()
        _username = args['username']
        _userEmail = args['email']
        _userPassword = args['password']

        if not _username or not _userEmail or not _userPassword:
            return {'Error': 'All fields are required'}, 400

        # Input validation
        if _username:
            _username = _username.lower()

        users = User.query.filter(User.username.ilike(
            _username) | User.email.ilike(_userEmail)).first()

        if users:
            return {'Error': 'Username or email already exists'}, 409

        email_regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

        if not email_regex.match(_userEmail):
            return {'Error': 'Not a valid email'}, 400

        if len(_userPassword) < 8 or len(_userPassword) > 15:
            return {'Message': 'Password should have 8-15 characters'}, 400

        try:
            user = User(_username,
                        _userEmail,
                        _userPassword,
                        )

            # User requires to authenticate account before account is activated
            user.active = False
            db.session.add(user)
            db.session.commit()

            return {'Message': 'New user registered successfully'}, 201

        except Exception as error:
            return {'error': str(error)}, 400
            db.session.flush()
            db.rollback()

    # @marshal_with(user_fields)
    # @requires_auth
    def get(self):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = User.query.filter_by(
            user_id=g.current_user).first()

        if user.role != "Admin":
            return {'Error': 'Unauthorised access'}, 401

        users = User.query.order_by(User.username).all()

        user_details = []

        if not users:
            return {'Warning': 'No users registered'}, 204

        for user in users:
            user_details.append({
                'user_id': user.user_id,
                'username': user.username.capitalize(),
                'email': user.email,
                'authenticated': user.authenticated,
                'active': user.active,
                'created_on': str(user.created_on),
            })

        return user_details, 200


class SingleUserAPI(Resource):
    """
    Single user resource

    endpoint: /bucketlist_api/v1.0/user/<int:id>
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str,
                                   help='User\'s username')
        self.reqparse.add_argument(
            "password", type=str, help='Password should have 8-15 characters')

        super(SingleUserAPI, self).__init__()

    def post(self, id):
        # The method is not allowed for the requested URL.
        return {'Error': 'Post not allowed for already existing user. Try PUT to edit user details'}, 405

    def get(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = User.query.filter_by(
            user_id=g.current_user).first()

        # Validate user to perform CRUD action on a user
        if (g.current_user != id and user.role != "Admin"):
            return {'Error Here:': 'Unauthorised access'}, 401

        # Fetch user from the DB
        users = User.query.filter_by(user_id=id).first()

        # Check is user exists
        if not users:
            return {'Error': 'User does not exist'}, 404

        user_details = {
            'user_id': users.user_id,
            'username': users.username,
            'email': users.email,
            'authenticated': users.authenticated,
            'active': users.active,
            'created_on': str(users.created_on),
        }

        return user_details, 200

    def put(self, id):
        args = self.reqparse.parse_args()

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = User.query.filter_by(
            user_id=g.current_user).first()

        # Validate user to perform CRUD action on a user
        if g.current_user != id:
            return {'Error': 'Unauthorised access'}, 401

        if not user:
            return {'Error': 'User does not exist'}, 404

        try:
            _username = args['username']
            _userPassword = args['password']

            if _username:
                # users = User.query.filter_by(
                #     username=_username).first()

                users = User.query.filter(
                    User.username.ilike(_username)).first()

                if users:
                    if users.username == _username:
                        return {'Error': 'Username not modified'}, 304

                    return {'Error': 'Username or email already exists'}, 409

                user.username = _username

            if _userPassword:
                if (len(_userPassword) < 8 or len(_userPassword) > 15):
                    db.session.rollback()
                    return {'Message': 'Password should have 8-15 characters'}, 400

                user.password = _userPassword

            db.session.commit()

            # Fetch updated record
            user = User.query.filter_by(user_id=id).first()
            user_details = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'authenticated': user.authenticated,
                'active': user.active,
                'created_on': str(user.created_on),
            }
            return user_details, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    def delete(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = User.query.filter_by(
            user_id=g.current_user).first()

        # Validate user to perform CRUD action on a user
        if user.role != "Admin":
            return {'Error': 'Unauthorised access'}, 401

        # Check if the user exists
        users = User.query.filter_by(user_id=id).first()

        if not users:
            return {'Error': 'User does not exist'}, 404

        _username = users.username

        try:
            # Delete bucketlist and bucketlist items for user
            bucketlists = Bucketlist.query.filter_by(created_by=id).all()

            for bucketlist in bucketlists:
                db.session.query(Bucketlist_Item).filter_by(
                    list_id=bucketlist.list_id).delete()

            db.session.query(Bucketlist).filter_by(created_by=id).delete()

            db.session.delete(users)
            db.session.commit()
            return {'Message': 'User {} deleted successfully'.format(_username)}, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400


class UserLoginAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True,
                                   help='No username provided')
        self.reqparse.add_argument(
            "password", type=str, required=True)

        super(UserLoginAPI, self).__init__()

    def post(self):

        args = self.reqparse.parse_args()
        _username = args['username']
        _userPassword = args['password']

        auth = False

        user = User.query.filter(User.username.ilike(
            _username)).first()

        auth = user.verify_password(_userPassword)
        _user_id = user.user_id

        if not auth:
            return {'Error': 'Incorrect login details'}, 401

        # Generate authentication token
        _token = generate_auth_token(_username, _user_id)

        return {'Message': 'Welcome {}'.format(_username),
                'Token': _token}, 200

    def get(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405

    def put(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405

    def delete(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405


class UserLogoutAPI(Resource):
    def post(self):
        pass

    def get(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405

    def put(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405

    def delete(self):
        # The method is not allowed for the requested URL.
        return {'Error': 'Method not allowed for login'}, 405
