import json
import re

from flask import g, request
from flask_restful import (
    Resource,
    reqparse
)
from werkzeug.wrappers import Response


from bucketlist.resources.authentication import (generate_auth_token,
                                                 verify_auth_token)
from bucketlist.app.models import db, User, Bucketlist, Bucketlist_Item
from bucketlist.app.serializer import UserSchema

user_schema = UserSchema()
users_schema = UserSchema(many=True)


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
        _username = args['username'].strip()
        _userEmail = args['email'].strip()
        _userPassword = args['password'].strip()

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
            user.active = True
            db.session.add(user)
            db.session.commit()

            return {'Message': 'New user registered successfully'}, 201

        except Exception as error:
            db.rollback()
            return {'Error': str(error)}, 400


class AllRegisteredUsers(Resource):
    def get(self):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = db.session.query(User).get(g.current_user)

        if user.admin is not True:
            return {'Error': 'Unauthorised access'}, 401

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'q',
            type=str,
            location='args',
            help='Search username'
        )
        self.reqparse.add_argument(
            'page',
            type=int,
            location='args',
            default=1,
            help='Page to start'
        )
        self.reqparse.add_argument(
            'limit',
            type=int,
            location='args',
            default=20,
            help='Results per page'
        )

        args = self.reqparse.parse_args()
        _query = args['q']
        _page = args['page']
        _limit = args['limit']

        if _limit and _limit > 100:
            return {'Error': 'Maximum number of results is 100'}, 400

        if _query:
            users = User.query.filter(User.admin.isnot(True),
                                      User.username.contains(
                                          '%' + _query + '%')
                                      ).order_by(
                User.username
            ).paginate(_page, _limit, False)

            if not users.items:
                return {
                    'Error': 'No users with the name/word {}'.format(_query)
                }, 404

        else:
            users = User.query.filter(
                User.admin.isnot(True)).order_by(
                User.username
            ).paginate(_page, _limit, False)

            if not users:
                return {'Warning': 'No users registered'}, 404

        if users.has_prev:
            prev_page = request.url_root + 'bucketlist_api/v1.0/users' \
                + '?page=' + str(_page - 1) + '&limit=' + str(_limit)
        else:
            prev_page = 'None'

        if users.has_next:
            next_page = request.url_root + 'bucketlist_api/v1.0/users' \
                + '?page=' + str(_page + 1) + '&limit=' + str(_limit)
        else:
            next_page = 'None'

        result = users_schema.dump(list(users.items))
        pages = {
            'message': {
                'prev_page': prev_page,
                'next_page': next_page,
                'total_pages': users.pages
            },
            'bucketlists': result.data
        }

        response = json.dumps(pages, sort_keys=False)

        return Response(
            response,
            status=200,
            mimetype='text/json'
        )

        # response = users_schema.jsonify(users)
        # response.status_code = 200
        # return response


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
        self.reqparse.add_argument("active", choices=('True', 'False'),
                                   help='True or False')

        super(SingleUserAPI, self).__init__()

    def post(self, id):
        # The method is not allowed for the requested URL.
        return {
            'Error': 'Method not allowed. Try PUT to edit user details'
        }, 405

    def get(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = db.session.query(User).get(g.current_user)

        # Validate user to perform CRUD action on a user
        if (g.current_user != id and user.admin is not True):
            return {'Error': 'Unauthorised access'}, 401

        # Fetch user from the DB
        users = User.query.filter_by(user_id=id).first()

        # Check is user exists
        if not users:
            return {'Error': 'User does not exist'}, 400

        response = user_schema.jsonify(users)
        response.status_code = 200
        return response

    def put(self, id):
        args = self.reqparse.parse_args()

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = db.session.query(User).get(g.current_user)

        # Validate user to perform CRUD action on a user
        if g.current_user != id:
            return {'Error': 'Unauthorised access'}, 401

        if not user:
            return {'Error': 'User does not exist'}, 400

        _username = args['username']
        _userPassword = args['password']
        _active = args['active']

        try:
            if _username:
                _username = _username.strip()

                users = User.query.filter(
                    User.username.ilike(_username)).first()

                if users:
                    if users.username == _username:
                        return {'Error': 'Username not modified'}, 304

                    return {'Error': 'Username or email already exists'}, 409

                user.username = _username

            if _userPassword:
                _userPassword = _userPassword.strip()

                if (len(_userPassword) < 8 or len(_userPassword) > 15):
                    db.session.rollback()
                    return {
                        'Message': 'Password should have 8-15 characters'
                    }, 400

                user.password = _userPassword

            if _active:
                _active = _active.strip()
                user.active = bool(_active)

            db.session.commit()

            # Fetch updated record
            user = User.query.filter_by(user_id=id).first()

            response = user_schema.jsonify(user)
            response.status_code = 200
            return response

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    def delete(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        user = db.session.query(User).get(g.current_user)

        # Validate user to perform CRUD action on a user
        if user.admin is not True:
            return {'Error': 'Unauthorised access'}, 401

        # Check if the user exists
        users = User.query.filter_by(user_id=id).first()

        if not users:
            return {'Error': 'User does not exist'}, 400

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
            return {
                'Message': 'User {} deleted successfully'.format(_username)
            }, 200

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
        _username = args['username'].strip()
        _userPassword = args['password'].strip()

        auth = False

        user = User.query.filter(User.username.ilike(
            _username)).first()

        auth = user.verify_password(_userPassword)
        _user_id = user.user_id

        if user.active is False:
            return {'Error': 'Account is deactivated'}, 400

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
