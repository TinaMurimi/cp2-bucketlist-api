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

        # Register and login new user
        self.register_response = self.client().post(
            '/bucketlist_api/v1.0/auth/register',
            data=self.user)

        self.login_response = self.client().post(
            '/bucketlist_api/v1.0/auth/login',
            data=self.user)

        self.response_json = json.loads(self.login_response.data.decode())
        self.header = {
            'Authorization': self.response_json['Token']}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_access(self):
        """Test user login"""

        self.assertEqual(self.login_response.status_code, 200)
        self.assertEqual(
            self.response_json['Message'], 'Welcome Lena'
        )
        self.assertTrue(isinstance(self.response_json['Token'], str))

    def test_token_validation(self):
        """Test token is velidated"""

        token = {
            'Authorization': 'Thisisaninvalidtoken'}

        # Test authorisation
        response = self.client().get('/bucketlist_api/v1.0/user/1',
                                     data=self.user,
                                     headers=token)
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

    def test_username_duplication(self):
        """Test user is not created with already existing username"""

        # Test username duplication
        self.user = {'username': 'Lena',
                     'email': 'lena.lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Username or email already exists', str(response.data))

    def test_email_duplication(self):
        """Test user is not created with already existing eamil"""

        # Test Email duplication
        self.user = {'username': 'Lena Dee',
                     'email': 'lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }
        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 400)

    def test_username_validation(self):
        """Test all fields are required"""

        self.user = {'username': '',
                     'email': '',
                     'password': '',
                     }

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertIn('All fields are required', str(response.data))

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

    def test_password_length(self):
        """Test password length"""

        # Test Email duplication
        self.user = {'username': 'Don',
                     'email': 'don@example.com',
                     'password': 'sfn',
                     }

        response = self.client().post('/bucketlist_api/v1.0/auth/register',
                                      data=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password should have 8-15 characters',
                      str(response.data))

    def test_get_all_users(self):
        """Test GET all users datails not allowed for normal user"""

        # Test authorisation
        response = self.client().get('/bucketlist_api/v1.0/auth/register',
                                     data=self.user,
                                     headers=self.header)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorised access', str(response.data))

    def test_post_not_allowed_fot_single_user_api(self):
        """Test POST method not allowed for single user api"""

        response = self.client().post('/bucketlist_api/v1.0/user/1',
                                      data=self.user)
        self.assertEqual(response.status_code, 405)

    def test_get_personal_user_details(self):
        """Test user can READ their details"""

        response = self.client().get('/bucketlist_api/v1.0/user/1',
                                     data=self.user,
                                     headers=self.header)
        self.assertEqual(response.status_code, 200)

    def test_update_user_details(self):
        """Test user can UPDATE their details"""

        self.new_details = {'username': 'Lena Dee',
                            }
        response = self.client().put(
            '/bucketlist_api/v1.0/user/1',
            data=self.new_details,
            headers=self.header)
        self.assertEqual(response.status_code, 200)

    def test_put_username_unique(self):
        """Test username is unique after update"""

        self.new_details = {
            'username': 'Lena',
        }

        response = self.client().put(
            '/bucketlist_api/v1.0/user/1',
            data=self.new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Username or email already exist', str(response.data))

    def test_put_password_length(self):
        """Test password length correctness on update"""

        self.new_details = {
            'password': 'Lena',
        }

        response = self.client().put(
            '/bucketlist_api/v1.0/user/1',
            data=self.new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Password should have 8-15 characters',
                      str(response.data))

    def test_user_delete(self):
        """Test user cannot DELETE their profile"""

        response = self.client().delete(
            '/bucketlist_api/v1.0/user/1',
            headers=self.header)
        # self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorised access', str(response.data))
