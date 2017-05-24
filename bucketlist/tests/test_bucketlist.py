import unittest
import json

from bucketlist.app import ConfigureApp
from bucketlist.app.models import db


class BucketlistTestCase(unittest.TestCase):
    def setUp(self):

        self.app = ConfigureApp(config_name="testing")
        db.init_app(self.app)

        # Create a test client
        self.client = self.app.test_client

        # Bind the app to the current context
        with self.app.app_context():
            db.drop_all()
            db.create_all()

        # User to use for bucketlist and items creation
        self.user = {'username': 'Lena',
                     'email': 'lena@andela.com',
                     'password': 'sfnbsdfiruio3r',
                     }

        lena = self.client().post('/bucketlist_api/v1.0/auth/register',
                                  data=self.user)

        login = self.client().post('/bucketlist_api/v1.0/auth/login',
                                   data=self.user)

        login_json = json.loads(login.data.decode())

        self.header = {
            'Authorization': login_json['Token']}

        # Create and login another user Don
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
            'Authorization': login_don_json["Token"]}

        # Bucketlist creation
        self.paragliding = {
            'bucketlist': 'Paragliding',
        }

        self.swimming = {
            'bucketlist': 'Dolphin swimming',
            'description': 'Go swimming with dolphins in Watamu, Kenya',
        }

        paragliding = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                         data=self.paragliding,
                                         headers=self.header)
        swimming = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.swimming,
                                      headers=self.header)

        # Bucketlist item creation
        self.paragliding_item = {
            'item': 'Iten Paragliding',
        }

        self.swimming_item = {
            'item': 'Go swimming',
        }

        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.paragliding_item,
            headers=self.header)

        # Bucketlist item update details
        self.item_new_details = {
            'item': 'Super Paragliding',
            'done': 'True'
        }

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_bucketlist_creation(self):
        """Test user can create a bucletlist"""

        # Bucketlist creation
        self.diving = {
            'bucketlist': 'Deep sea diving',
        }

        response = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.diving,
                                      headers=self.header)

        self.assertEqual(response.status_code, 201)
        self.assertIn('Bucketlist added successfully successfully',
                      str(response.data))

    def test_bucketlist_name_validation(self):
        """Test bucketlist name is validated"""

        self.bungee = {
            'bucketlist': '',
        }

        response = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.bungee,
                                      headers=self.header)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Bucketlist name is required',
            str(response.data))

    def test_bucketlist_duplication(self):
        """Test bucketlist name is unique"""

        response = self.client().post('/bucketlist_api/v1.0/bucketlists',
                                      data=self.paragliding,
                                      headers=self.header)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Bucketlist already exists',
            str(response.data))

    def test_get_all_bucketlists(self):
        """Test user can get list od all bucketlists"""

        response = self.client().get('bucketlist_api/v1.0/bucketlists',
                                     headers=self.header)
        self.assertEqual(response.status_code, 200)

    def test_get_search_bucketlists(self):
        """
        Test GET searching for bucket lists based on the name
        """
        response = self.client().get('bucketlist_api/v1.0/bucketlists?q=par',
                                     headers=self.header)
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        """
        Test GET searching for bucket lists based on the name that does not
        have a match
        """

        response = self.client().get('bucketlist_api/v1.0/bucketlists?q=bucketlist',
                                     headers=self.header)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'No bucketlists with the word bucketlist',
            str(response.data))

    def test_get_pagination_bucketlists(self):
        """
        Test pagination
        """

        response = self.client().get('bucketlist_api/v1.0/bucketlists?limit=1',
                                     headers=self.header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Paragliding', str(response.data))

    def test_get_bucketlist_exists(self):
        """
        Test READ operation works only if bucketlist exists
        """

        response = self.client().get('/bucketlist_api/v1.0/bucketlists/5',
                                     headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            'Bucketlist does not exist',
            str(response.data))

    def test_put_bucketlist_exists(self):
        """
        Test UPDATE operation works only if bucketlist exists
        """

        self.new_details = {
            'bcuketlist': 'Dolphin swimming'
        }

        response = self.client().put('/bucketlist_api/v1.0/bucketlists/5',
                                     data=self.new_details,
                                     headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            'Bucketlist does not exist',
            str(response.data))

    def test_put_bucketlist_name_unique(self):
        """
        Test bucketlist name is unique when updating
        """

        self.new_details = {
            'bucketlist': 'Dolphin swimming'
        }

        response = self.client().put('/bucketlist_api/v1.0/bucketlists/2',
                                     data=self.new_details,
                                     headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Bucketlist already exists',
            str(response.data))

    def test_put_bucketlist_done(self):
        """
        Test bucketlist cannot be updated to complete if items are incomplete
        """

        self.new_details = {
            'done': 'True'
        }

        response = self.client().put(
            '/bucketlist_api/v1.0/bucketlists/1',
            data=self.new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            'Bucketlist has incomplete items/activities',
            str(response.data))

    def test_get_bucketlist(self):
        """
        Test user can view their bucketlist items
        """

        response = self.client().get('/bucketlist_api/v1.0/bucketlists/1',
                                     headers=self.header)

        self.assertEqual(response.status_code, 200)

    def test_update_bucketlist(self):
        """
        Test user can update bucketlist
        """

        self.new_details = {
            'bucketlis': 'Iten Tea trip'
        }

        response = self.client().put('/bucketlist_api/v1.0/bucketlists/1',
                                     data=self.new_details,
                                     headers=self.header)

        self.assertEqual(response.status_code, 200)

    def test_delete_bucketlist(self):
        """
        Test user can delete bucketlist
        """

        response = self.client().delete('/bucketlist_api/v1.0/bucketlists/1',
                                        data=self.paragliding,
                                        headers=self.header)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Bucketlist deleted successfully', str(response.data))

    def test_bucketlist_get_access(self):
        """
        Test user can only perform READ operation on their bucketlist
        """

        # Test GET
        response = self.client().get('/bucketlist_api/v1.0/bucketlists/1',
                                     headers=self.header_don)
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            'Unauthorised access', str(response.data))

    def test_bucketlist_put_access(self):
        """
        Test user can only perform UPDATE operation on their bucketlist
        """

        # Test PUT
        self.new_details = {
            'bucketlis': 'Iten Tea trip'
        }

        response = self.client().put('/bucketlist_api/v1.0/bucketlists/1',
                                     data=self.new_details,
                                     headers=self.header_don)

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            'Unauthorised access', str(response.data))

    def test_bucketlist_delete_access(self):
        """
        Test user can only perform DELETE operation on their bucketlist
        """

        # Test DELETE
        response = self.client().delete(
            '/bucketlist_api/v1.0/bucketlists/1',
            data=self.paragliding,
            headers=self.header_don)

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            'Unauthorised access', str(response.data))

    def test_bucketlist_item_creation(self):
        """Test user can create a bucketlist item"""

        # Bucketlist item creation
        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.swimming_item,
            headers=self.header)

        self.assertEqual(response.status_code, 201)
        self.assertIn(
            'Bucketlist item added successfully successfully',
            str(response.data))

    def test_bucketlist_item_name_validation(self):
        """
        Test bucketlist item name is validated
        """

        self.fishing = {
            'item': ''
        }

        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.fishing,
            headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Bucketlist item name is required", str(response.data))

    def test_bucketlist_id_for_item_creation(self):
        """
        Test bucketlist item can only be created in existing bucket list
        """

        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/5/items',
            data=self.swimming_item,
            headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Bucketlist does not exist", str(response.data))

    def test_user_owns_bucketlist(self):
        """
        Test user must own bucketlist to create item in
        """

        # Add item to Lena's bucketlist
        response_don = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.swimming_item,
            headers=self.header_don)
        self.assertEqual(response_don.status_code, 401)
        self.assertIn(
            'Unauthorised access', str(response_don.data))

    def test_post_bucketlist_item_name_unique(self):
        """
        Test bucketlist item name is unique (POST)
        """

        self.item = {
            'item': 'Iten Paragliding',
        }

        response = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.item,
            headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Bucketlist item already exists", str(response.data))

    def test_get_bucketlist_item(self):
        """
        Test user can READ single bucketlist item
        """

        response = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/1/items/1',
            headers=self.header)

        self.assertEqual(response.status_code, 200)

    def test_get_bucketlist_item_exists(self):
        """
        Test user can READ single bucketlist item that exists
        """

        response = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/1/items/12',
            headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn('Bucketlist item does not exist', str(response.data))

    def test_put_bucketlist_item_exists(self):
        """
        Test user can UPDATE single bucketlist item that exists
        """

        response = self.client().get(
            '/bucketlist_api/v1.0/bucketlists/1/items/12',
            data=self.item_new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn('Bucketlist item does not exist', str(response.data))

    def test_put_bucketlist_item(self):
        """
        Test bucketlist item update
        """

        response = self.client().put(
            '/bucketlist_api/v1.0/bucketlists/1/items/1',
            data=self.item_new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 200)

    def test_put_bucketlist_item_name_unique(self):
        """
        Test bucketlist item name is unique when updating
        """

        swimming_item_post = self.client().post(
            '/bucketlist_api/v1.0/bucketlists/1/items',
            data=self.swimming_item,
            headers=self.header)

        self.item_new_details = {
            'item': 'Iten Paragliding',
        }

        response = self.client().put(
            '/bucketlist_api/v1.0/bucketlists/1/items/2',
            data=self.item_new_details,
            headers=self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Bucketlist item already exists', str(response.data))

    def test_delete_bucketlist_item(self):
        """
        Test user can delete a bucketlist item
        """

        response = self.client().delete(
            '/bucketlist_api/v1.0/bucketlists/1/items/1',
            headers=self.header)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Bucketlist item deleted successfully',
                      str(response.data))

    def test_delete_bucketlist_item_exists(self):
        """
        Test user can delete a bucketlist item that exists
        """

        response = self.client().delete(
            '/bucketlist_api/v1.0/bucketlists/1/items/12',
            headers=self.header)

        self.assertEqual(response.status_code, 404)
        self.assertIn('Bucketlist item does not exist', str(response.data))
