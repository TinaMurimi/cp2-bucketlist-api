import unittest
import os
import json

from flask.testing import FlaskClient

from bucketlist.app import ConfigureApp
from bucketlist.app.models import db, User


class UserTestCase(unittest.TestCase):
    def setUp(self):

        self.app = ConfigureApp(config_name="testing")
        db.init_app(self.app)

        # Create a test client
        self.client = self.app.test_client

        # Propagate the exceptions to the test client
        # self.client.testing = True

        self.user = {'username': 'Lena',
                     'email': 'lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }

        # Bind the app to the current context
        with self.app.app_context():
            db.create_all()

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_access(self):
        """Test user cannot access another user's bucketlist"""
        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data=self.user)
        response_json = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response_json['Message'], 'Welcome Lena'
        )
        self.assertTrue(isinstance(response_json['Token'], bytes))

    def test_token_validation(self):
        """Test token is velidated"""

        header = {
            'Authorization': 'Thisisaninvalidtoken'}

        # Test authorisation
        response = self.client().get('/bucketlist_api/v1.0/auth/register',
                                     data=self.user,
                                     headers=header)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token. Please log in again', str(response.data))

    def test_user_creation(self):
        """Test API can create a user (POST request)"""
        self.don = {'username': 'don',
                    'email': 'don@andela.com',
                    'password': 'sfnbsdfiruio3r',
                    }
        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.don)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New user registered successfully', str(response.data))

    def test_user_duplication(self):
        """Test user is not created with already existing username/password"""

        # Test username duplication
        self.user = {'username': 'Lena',
                     'email': 'lena.lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Username or email already exists', str(response.data))

        # Test Email duplication
        self.user = {'username': 'Lena',
                     'email': 'lena.lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }
        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 409)

    def test_email_validation(self):
        """Test email validation"""

        # Test Email duplication
        self.user = {'username': 'Don',
                     'email': 'don',
                     'password': 'sfnbsdfiruio3r',
                     }

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Not a valid email', str(response.data))

    def test_get_all_users(self):
        """Test GET all users datails not allowed for normal user"""

        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data=self.user)

        response_json = json.loads(response.data.decode())
        header = {
            'Authorization': response_json['Token']}

        # Test authorisation
        response = self.client().get('/bucketlist_api/v1.0/auth/register',
                                     data=self.user,
                                     headers=header)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorised access', str(response.data))

    def test_post_not_allowed_fot_single_user_api(self):
        """Test POST method not allowed for single user api"""

        response = self.client().post('/bucketlist_api/v1.0/user/1',
                                      data=self.user)
        self.assertEqual(response.status_code, 405)

    def test_get_user_profile(self):
        """Test user can READ their details"""

        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data=self.user)

        response_json = json.loads(response.data.decode())
        header = {
            'Authorization': response_json['Token']}

        response = self.client().get('/bucketlist_api/v1.0/user/1',
                                     data=self.user,
                                     headers=header)
        self.assertEqual(response.status_code, 200)

    def test_update_user_profile(self):
        """Test user can UPDATE their details"""

        self.new_details = {'username': 'Lena Dee',
                            }

        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data=self.user)

        response_json = json.loads(response.data.decode())
        header = {
            'Authorization': response_json['Token']}

        response = self.client().put('/bucketlist_api/v1.0/user/1',
                                     data=self.new_details,
                                     headers=header)
        self.assertEqual(response.status_code, 200)

    def test_user_delete(self):
        """Test user cannot DELETE their profile"""

        response = self.client().post('/bucketlist_api/v1.0/auth/login',
                                      data=self.user)

        response_json = json.loads(response.data.decode())
        header = {
            'Authorization': response_json['Token']}

        response = self.client().delete('/bucketlist_api/v1.0/user/1',
                                        data=self.user,
                                        headers=header)
        # self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorised access', str(response.data))
