import re

from sqlalchemy import or_

from flask import Flask, g, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from itsdangerous import TimedJSONWebSignatureSerializer as JTW

from bucketlist.app import app, api
from bucketlist.app.models import auth, db, User, Bucketlist_Item

# Create an instance of Bcyrpt
bcrypt = Bcrypt(app)

jwt = JWT(app.config['SECRET_KEY'], expires_in=60 * 60)
# auth = HTTPTokenAuth('Bearer')

user_fields = {
    'user_id':  fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
}


class UserRegistrationAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str, required=True,
                                   help='No username provided')
        self.reqparse.add_argument(
            "email", type=str, required=True)
        self.reqparse.add_argument(
            "password", type=str, required=True)

        super(UserRegistrationAPI, self).__init__()

    def post(self):

        try:
            args = self.reqparse.parse_args()
            _username = args['username']
            _userEmail = args['email']
            _userPassword = args['password']

            db_user = User.query.filter(
                (User.username == _username) | (User.email == _userEmail)).first()
            # db_user = filter(or_(User.username == _username, User.email == _userEmail))

            if not _username or not _userEmail or not _userPassword:
                return {'Error': 'All fields are required'}, 400
            else:
                if db_user:
                    return {'Error': 'Username or email already exists'}, 400

                email_regex = re.compile(
                    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

                if not email_regex.match(_userEmail):
                    return {'Error': 'Not a valid email'}, 400

                if len(_userPassword) < 8 or len(_userPassword) > 15:
                    return {'Message': 'Password should have 8-15 characters'}, 400

            user = User(_username,
                        _userEmail,
                        _userPassword,
                        'User'
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
    def get(self):
        # args = self.reqparse.parse_args()
        users = User.query.order_by(User.username).all()
        user_details = []

        if not users:
            return {'Warning': 'No users registered'}, 204

        for user in users:
            user_details.append({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'authenticated': user.authenticated,
                'active': user.active,
                'created_on': user.created_on,
            })

        return jsonify(user_details)


class SingleUserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("username", type=str,
                                   help='User\'s username')
        self.reqparse.add_argument(
            "password", type=str, help='Password should have 8-15 characters')

        super(SingleUserAPI, self).__init__()

    def get(self, id):
        user = User.query.filter_by(user_id=id).first()

        if not user:
            return {'Error': 'User does not exist'}, 404

        user_details = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'authenticated': user.authenticated,
            'active': user.active,
            'created_on': str(user.created_on),
        }

        _response = jsonify(user_details)
        _response.status_code = 201

        # return {'user': user_details}, 201
        # return _response
        return user_details, 201

    def put(self, id):
        args = self.reqparse.parse_args()

        user = User.query.filter_by(user_id=id).first()

        if not user:
            return {'Error': 'User does not exist'}, 404

        try:
            _username = args['username']
            _userPassword = args['password']

            if _username:
                user.username = _username

            if _userPassword:
                if (len(_userPassword) < 8 or len(_userPassword) > 15):
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
        # user = User.query.get_or_404(id)
        user = User.query.filter_by(user_id=id).first()

        # try:
        if not user:
            return {'Error': 'User does not exist'}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            response = make_response()
            response.status_code = 204
            return {'Message': 'User deleted successfully'}, 204

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400


class BucketlistAPI(Resource):
    def post(self, id):
        pass

    def get(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        pass


api.add_resource(UserRegistrationAPI,
                 '/bucketlist_api/v1.0/auth/user', endpoint='register_user')
api.add_resource(SingleUserAPI,
                 '/bucketlist_api/v1.0/auth/user/<int:id>', endpoint='single_user')
