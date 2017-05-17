import unittest
import os
import json

from flask.testing import FlaskClient

from bucketlist.app import ConfigureApp
from bucketlist.app.models import db


class BucketlistTest(unittest.TestCase):
    def setUp(self):

        self.app = ConfigureApp(config_name="testing")

        # Create a test client
        self.client = self.app.test_client

        # # Propagate the exceptions to the test client
        # self.client.testing = True

        self.user = {'username': 'Tina',
                     'email': 'tina.murimi@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }
        self.bucketlist = {'list_name': 'Go paragliding in Iten',
                           'created_by': '1',
                           }
        # Bind the app to the current context
        with self.app.app_context():
            db.init_app(self.app)
            db.create_all()

    def tearDown(self):
        pass
        # db.session.remove()
        # db.drop_all()

    def test_user_creation(self):
        """Test API can create a user (POST request)"""
        response = self.client().post('/bucketlist_api/v1.0/auth/user', data=self.user)
        # self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', str(response.data))

    # def test_bucketlist_creation(self):
    #     """Test API can create a bucketlist (POST request)"""
    #     result = self.client().post('/bucketlist/', data=self.bucketlist)
    #     self.assertEqual(result.status_code, 201)
    #     self.assertIn('Go paragliding in Iten', str(result.data))
