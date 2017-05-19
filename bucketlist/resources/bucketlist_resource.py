import json

from datetime import date
from flask import Flask, g, jsonify, make_response, request
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from functools import wraps
from sqlalchemy import func

from bucketlist.app.models import auth, db, User, Bucketlist, Bucketlist_Item
from bucketlist.resources.views import verify_auth_token


user_fields = {
    'user_id':  fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
}

RESULTS_PER_PAGE = 20


class BucketlistAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("bucketlist", type=str,
                                   help='Bucketlist name')
        self.reqparse.add_argument("description", type=str,
                                   help='Bucketlist description')

        super(BucketlistAPI, self).__init__()

    def post(self):
        """
        Add a new bucketlist

        Attributes:
        - list_name (required): A string representing the bucketlist's name
        - description (optional): A string representing the bucketlist's description
        - created_by (required): An foreign key from table User representing owner of bucketlist
        """

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) != int:
            return g.current_user

        # try:
        args = self.reqparse.parse_args()
        _bucketlist = args['bucketlist']
        _description = args['description']

        bucketlists = Bucketlist.query.filter(Bucketlist.created_by == g.current_user,
                                              Bucketlist.list_name.ilike(_bucketlist)).first()

        # Validate the bucketlist name
        if not _bucketlist:
            return {'Error': 'Bucketlist name is required'}, 400

        if _bucketlist.isdigit() or len(_bucketlist) < 5 or len(_bucketlist) > 20:
            return {'Error': 'Invalid bucketlist name or length (5-20 characters)'}, 400

        if bucketlists:
            return {'Error': 'Bucketlist already exists'}, 409

        if _description:
            _description = _description.capitalize()

        bucketlist = Bucketlist(list_name=_bucketlist.capitalize(),
                                description=_description,
                                created_by=g.current_user,
                                )

        # Persist to DB
        db.session.add(bucketlist)
        db.session.commit()

        return {'Message': 'Bucketlist added successfully successfully'}, 201

        # except Exception as error:
        #     return {'Error': str(error)}, 400
        #     db.session.flush()
        #     db.rollback()

    # @requires_auth
    def get(self):
        """
        Returns a list of all bucketlists for a particular user
        """

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) != int:
            return g.current_user

        bucketlists = Bucketlist.query.filter_by(
            created_by=g.current_user).all()

        bucketlist_details = []

        if not bucketlists:
            return {'Warning': 'No bucketlists available for current user'}, 204

        for bucketlist in bucketlists:
            bucketlist_details.append({
                'id': bucketlist.list_id,
                'name': bucketlist.list_name,
                'description': bucketlist.description,
                'is_completed': bucketlist.is_completed,
                'date_created': str(bucketlist.created_on),
                'date_modified': str(bucketlist.date_modified),
                'created_by': bucketlist.created_by,
            })

        return bucketlist_details, 200


class SingleBucketlistAPI(Resource):
    """
    Single bucketlist reource

    route: /bucketlist_api/v1.0/bucketlists/<int:id>
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("bucketlist", type=str,
                                   help='Edit bucketlist name')
        self.reqparse.add_argument("description", type=str,
                                   help='Edit bucketlist description')
        self.reqparse.add_argument("done", choices=('True', 'False'),
                                   help='True or False')

        super(SingleBucketlistAPI, self).__init__()

    def post(self, id):
        return {'Error': 'Method not allowed. Use /bucketlist_api/v1.0/bucketlists'}, 405

    def get(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) != int:
            return g.current_user

        # Validate user to perform CRUD action on a bucketlist
        bucketlists = Bucketlist.query.filter_by(
            list_id=id).first()

        # Check if bucketlist exists
        if not bucketlists:
            return {'Error': 'Bucketlist does not exist'}, 404

        if g.current_user != bucketlists.created_by:
            return {'Error': 'Unauthorised access'}, 401

        try:
            items = Bucketlist_Item.query.join(Bucketlist,
                                               (Bucketlist_Item.list_id == Bucketlist.list_id)). \
                filter(Bucketlist.list_id == id). \
                all()

            bucketlist_details = {
                'id': bucketlists.list_id,
                'name': bucketlists.list_name,
                'description': bucketlists.description,
                'items': ['No bucketlist items available'],
                'date_created': str(bucketlists.created_on),
                'date_modified': str(bucketlists.date_modified),
                'created_by': bucketlists.created_by,
                'done': bucketlists.is_completed,
            }

            item_details = []
            if items:
                for item in items:
                    item_details.append({
                        'id': item.item_id,
                        'name': item.item_name,
                        'date_created': str(item.created_on),
                        'date_modified': str(item.date_modified),
                        'done': item.is_completed,
                    })

                bucketlist_details['items'] = item_details

            return bucketlist_details, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    def put(self, id):

        args = self.reqparse.parse_args()

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        # Validate user to perform CRUD action on a bucketlist
        bucketlists = Bucketlist.query.filter_by(
            list_id=id).first()

        # Check if bucketlist exists
        if not bucketlists:
            return {'Error': 'Bucketlist does not exist'}, 404

        if g.current_user != bucketlists.created_by:
            return {'Error': 'Unauthorised access'}, 401

        _bucketlist = args['bucketlist']
        _description = args['description']
        _done = args['done']

        try:
            if _bucketlist:
                if _bucketlist.isdigit() or len(_bucketlist) < 5 or len(_bucketlist) > 20:
                    return {'Error': 'Invalid bucketlist name or length (5-20 characters)'}, 400

                bucketlist = Bucketlist.query.filter(Bucketlist.list_name.ilike(
                    _bucketlist),
                    Bucketlist.created_by == g.current_user).first()

                if bucketlist and _bucketlist.lower() == bucketlist.list_name.lower():
                    return {'Message': 'Bucketlist name not modified'}, 304

                # Before updating, check if the bucketlist exists
                if bucketlist:
                    return {'Error': 'Bucketlist already exists'}, 409

                bucketlists.list_name = _bucketlist.capitalize()

            if _description:
                bucketlists.description = _description.capitalize()

            if _done is not None and bool(_done):
                # Check if bucketlist items are all done
                incomplete_items = Bucketlist_Item.query.filter(
                    Bucketlist_Item.list_id == id,
                    Bucketlist.is_completed.is_(False)).first()

                if incomplete_items:
                    return {'Error': 'Bucketlist has incomplete items/activities'}, 403
                else:
                    return 'Here'

            bucketlists.is_completed = bool(_done)

            # Update date_modified
            bucketlists.date_modified = date.today().isoformat()

            # Commit changes
            db.session.commit()

            # Fetch updated record
            bucketlists = Bucketlist.query.filter_by(
                list_id=id).first()

            bucketlist_details = {
                'id': bucketlists.list_id,
                'name': bucketlists.list_name,
                'description': bucketlists.description,
                'date_created': str(bucketlists.created_on),
                'date_modified': str(bucketlists.date_modified),
                'created_by': bucketlists.created_by,
                'done': bucketlists.is_completed,
            }
            return bucketlist_details, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    # @requires_auth
    def delete(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if type(g.current_user) is not int:
            return g.current_user

        # Validate user to perform CRUD action on a bucketlist
        bucketlist = Bucketlist.query.filter_by(
            list_id=id).first()

        # Check if bucketlist exists
        if not bucketlist:
            return {'Error': 'Bucketlist does not exist'}, 404

        if g.current_user != bucketlist.created_by:
            return {'Error': 'Unauthorised access'}, 401

        # try:
        # Delete bucketlist items for bucketlist
        db.session.query(Bucketlist_Item).filter(
            Bucketlist_Item.list_id == id).delete()

        db.session.delete(bucketlist)
        db.session.commit()
        return {'Message': 'Bucketlist deleted successfully'}, 200

        # except Exception as error:
        #     db.session.rollback()
        #     return {'Error': str(error)}, 400


def validate_access(self, bucketlist_id, bucketlistitem_id=None):
    """
    Check if user has authorisation to perform CRUD on bucketlist item

    returns set,tuple: if error/warning else int (current_user)
    """

    # Validate token
    _token = request.headers.get("Authorization")
    g.current_user = verify_auth_token(_token)

    if type(g.current_user) is not int:
        return g.current_user

    # Validate user to perform CRUD action on a bucketlist
    bucketlist = Bucketlist.query.filter_by(
        list_id=bucketlist_id).first()

    # Check if bucketlist exists
    if not bucketlist:
        return {'Error': 'Bucketlist does not exist'}, 404

    if g.current_user != bucketlist.created_by:
        return {'Error': 'Unauthorised access'}, 401

    # Check if bucketlist item exists
    if bucketlistitem_id:
        items = Bucketlist_Item.query.filter_by(list_id=bucketlist_id,
                                                item_id=bucketlistitem_id).first()

        if not items:
            return {'Error': 'Bucketlist item does not exist'}, 404

    return g.current_user


class BucketlistItemAPI(Resource):
    """
    Single bucketlist item resource

    route: /bucketlist_api/v1.0/bucketlists/<int:id>/items
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("item", type=str,
                                   help='Bucketlist item name')
        self.reqparse.add_argument("description", type=str,
                                   help='Bucketlist item description')

        super(BucketlistItemAPI, self).__init__()

    def post(self, id):
        """
        Add a new bucketlist item

        Attributes:
        - item_name (required): A string representing the bucketlist item's name
        - description (optional): A string representing the bucketlist item's description
        - list_id (required): An foreign key from table Bucketlist representing bucketlist id
        """

        # Validate user to perform CRUD action on a bucketlist
        current_user = validate_access(self, id)

        if isinstance(current_user, (tuple, set)):
            return current_user

        args = self.reqparse.parse_args()
        _item = args['item']
        _description = args['description']

        items = Bucketlist_Item.query.filter(
            Bucketlist_Item.list_id == id,

            Bucketlist_Item.item_name.ilike(_item)).first()

        if not _item:
            return {'Error': 'Bucketlist item name is required'}, 400

        if _item.isdigit() or len(_item) < 5 or len(_item) > 20:
            return {'Error': 'Invalid bucketlist name or length (5-20 characters)'}, 400

        if items:
            return {'Error': 'Bucketlist item already exists'}, 409

        # Check if bucketlist exists
        items = Bucketlist.query.filter(
            Bucketlist.list_id == id).first()

        if not items:
            return {'Error': 'Bucketlist does not exists'}, 400

        try:

            item = Bucketlist_Item(item_name=_item,
                                   description=_description,
                                   list_id=id,
                                   )

            # Persist to DB
            db.session.add(item)
            db.session.commit()

            return {'Message': 'Bucketlist item added successfully successfully'}, 201

        except Exception as error:
            return {'Error': str(error)}, 400
            db.session.flush()
            db.rollback()

    def get(self, id):
        """
        Method not allowed for single bucketlist item
        """

        return {'Error': 'Mehtod not allowed. Use /bucketlist_api/v1.0/bucketlists/<int:id>'}, 405


class SingleBucketlistItemAPI(Resource):
    """
    Single bucketlist item resource

    /bucketlist_api/v1.0/bucketlists/<int:id>/items/<int:item_id>
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("item", type=str,
                                   help='Bucketlist item name')
        self.reqparse.add_argument("description", type=str,
                                   help='Bucketlist item description')
        self.reqparse.add_argument("done", type=bool,
                                   help='Have you done/completed the bucketlist item?')
        self.reqparse.add_argument("bucketlist_id", type=int,
                                   help='Reassign a wrongly placed bucketlist item')

        super(SingleBucketlistItemAPI, self).__init__()

    def post(self, id, item_id):
        return {'Error': 'Method not allowed. Use /bucketlist_api/v1.0/bucketlists/<int:id>/items'}, 405

    def get(self, id, item_id):

        # Validate user access
        current_user = validate_access(self, id, item_id)

        if not str(current_user).isdigit():
            return current_user

        items = Bucketlist_Item.query.filter_by(list_id=id,
                                                item_id=item_id).first()

        try:

            item_details = {
                'id': items.item_id,
                'list_id': items.list_id,
                'name': items.item_name,
                'description': items.description,
                'date_created': str(items.created_on),
                'date_modified': str(items.date_modified),
                'done': items.is_completed,
            }

            return item_details, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    def put(self, id, item_id):

        args = self.reqparse.parse_args()

        # Validate user access
        current_user = validate_access(self, id, item_id)

        if not str(current_user).isdigit():
            return current_user

        _item = args['item']
        _description = args['description']
        _done = args['done']
        _bucketlist_id = args['bucketlist_id']

        items = Bucketlist_Item.query.filter(Bucketlist_Item.item_id == item_id,
                                             Bucketlist_Item.list_id == id).first()

        if _item:
            if _item.isdigit() or len(_item) < 5 or len(_item) > 20:
                return {'Error': 'Invalid bucketlist name or length (5-20 characters)'}, 400

            item = Bucketlist_Item.query.filter(Bucketlist_Item.list_id == id,
                                                Bucketlist_Item.item_name.ilike(_item)).first()

            # Before updating, check if the bucketlist exists
            if item:
                return {'Error': 'Bucketlist item already exists'}, 409

            items.item_name = _item

        if _description:
            items.description = _description

        if _done:
            items.is_completed = _done

        if _bucketlist_id:
            items.list_id = _bucketlist_id

        # Update date_modified
        items.date_modified = date.today().isoformat()

        try:

            # Commit changes
            db.session.commit()

            # Fetch updated record
            items = Bucketlist_Item.query.filter_by(
                item_id=item_id).first()

            item_details = {
                'id': items.item_id,
                'list_id': items.list_id,
                'name': items.item_name,
                'description': items.description,
                'date_created': str(items.created_on),
                'date_modified': str(items.date_modified),
                'done': items.is_completed,
            }
            return item_details, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400

    def delete(self, id, item_id):

        # Check if bucketlist item exists
        items = Bucketlist_Item.query.filter_by(
            item_id=item_id).first()

        if not items:
            return {'Error': 'Bucketlist item does not exist'}, 404

        try:
            db.session.delete(items)
            db.session.commit()
            return {'Message': 'Bucketlist item deleted successfully'}, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400
