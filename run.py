from flask_restful import Api

from bucketlist.app import app
from bucketlist.app.resource import UserRegistrationAPI, SingleUserAPI

api = Api(app)

# Register the routes with the framework using the given endpoint
api.add_resource(UserRegistrationAPI,
                 '/bucketlist_api/v1.0/auth/user', endpoint='register_user')
api.add_resource(SingleUserAPI,
                 '/bucketlist_api/v1.0/auth/user/<int:id>', endpoint='single_user')

if __name__ == '__main__':
    app.run()