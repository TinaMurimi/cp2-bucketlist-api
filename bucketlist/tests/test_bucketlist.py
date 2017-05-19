import unittest
import os
import json

from flask.testing import FlaskClient

from bucketlist.app import ConfigureApp
from bucketlist.app.models import db, User, Bucketlist, Bucketlist_Item


class BucketlistTestCase(unittest.TestCase):
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

        self.bucketlist = {
            'bucketlist': 'Paragliding',
        }

        self.item = {
            'item': 'Iten Paragliding',
        }

        # Bind the app to the current context
        with self.app.app_context():
            db.create_all()

        # User to use for bucketlist and items creation
        lena = self.client().post('/bucketlist_api/v1.0/auth/register',
                                  data=self.user)

        login = self.client().post('/bucketlist_api/v1.0/auth/login',
                                   data=self.user)

        login_json = json.loads(login.data.decode())
        self.header = {
            'Authorization': login_json['Token']}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_bucketlist_and_item_creation(self):
        """Test user can create a bucletlist and bucketlist item"""

        # Bucketlist creation
        response = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.bucketlist,
                                      headers=self.header)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Bucketlist added successfully successfully',
                      str(response.data))

        # Bucketlist item creation
        response = self.client().post('/bucketlist_api/v1.0/bucketlists/1/items',
                                      data=self.item,
                                      headers=self.header)
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            'Bucketlist item added successfully successfully', str(response.data))

    def test_bucketlist_id(self):
        """
        Test bucketlist item can only be created in existing bucket list
        """

        response = self.client().post('/bucketlist_api/v1.0/bucketlists/2/items',
                                      data=self.item,
                                      headers=self.header)

        # self.assertEqual(response.status_code, 201)
        self.assertIn(
            'Bucketlist does not exists', str(response.data))

    def test_user_owns_bucketlist(self):
        """
        Test user must own bucketlist to create item in
        """

        response = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.bucketlist,
                                      headers=self.header)

        # Create and login new user
        self.don = {'username': 'Don',
                    'email': 'don@andela.com',
                    'password': 'sfnbsdfiruio3r',
                    }

        don = self.client().post('/bucketlist_api/v1.0/auth/register',
                                 data=self.don)

        login_don = self.client().post('/bucketlist_api/v1.0/auth/login',
                                       data=self.don)

        login_don_json = json.loads(login_don.data.decode())
        self.header_don = {
            'Authorization': login_don_json['Token']}

        # Add item to Lena's bucketlist
        response_don = self.client().post('/bucketlist_api/v1.0/bucketlists/1/items',
                                          data=self.item,
                                          headers=self.header_don)
        self.assertEqual(response_don.status_code, 401)
        self.assertEqual(
            'Unauthorised access', str(response_don.data))

    # def test_post_not_allowed_fot_single_user_api(self):
    #     """Test POST method not allowed for single user api"""

    #     response = self.client().post('/bucketlist_api/v1.0/user/1',
    #                                   data=self.user)
    #     self.assertEqual(response.status_code, 405)

    # def test_get_user_profile(self):
    #     """Test user can READ their details"""

    #     response = self.client().post('/bucketlist_api/v1.0/auth/login',
    #                                   data=self.user)

    #     response_json = json.loads(response.data.decode())
    #     header = {
    #         'Authorization': response_json['Token']}

    #     response = self.client().get('/bucketlist_api/v1.0/user/1',
    #                                  data=self.user,
    #                                  headers=header)
    #     self.assertEqual(response.status_code, 200)

    # def test_update_user_profile(self):
    #     """Test user can UPDATE their details"""

    #     self.new_details = {'username': 'Lena Dee',
    #                         }

    #     response = self.client().post('/bucketlist_api/v1.0/auth/login',
    #                                   data=self.user)

    #     response_json = json.loads(response.data.decode())
    #     header = {
    #         'Authorization': response_json['Token']}

    #     response = self.client().put('/bucketlist_api/v1.0/user/1',
    #                                  data=self.new_details,
    #                                  headers=header)
    #     self.assertEqual(response.status_code, 200)

    # def test_user_delete(self):
    #     """Test user cannot DELETE their profile"""

    #     response = self.client().post('/bucketlist_api/v1.0/auth/login',
    #                                   data=self.user)

    #     response_json = json.loads(response.data.decode())
    #     header = {
    #         'Authorization': response_json['Token']}

    #     response = self.client().delete('/bucketlist_api/v1.0/user/1',
    #                                     data=self.user,
    #                                     headers=header)
    #     # self.assertEqual(response.status_code, 401)
    #     self.assertIn('Unauthorised access', str(response.data))
