import json

from datetime import datetime
from flask import g, request
from flask_restful import Resource, reqparse
from werkzeug.wrappers import Response


from bucketlist.app.models import db, Bucketlist, Bucketlist_Item
from bucketlist.resources.authentication import verify_auth_token
from bucketlist.app.serializer import BucketlistSchema, BucketlistItemSchema

bucketlist_schema = BucketlistSchema()
bucketlists_schema = BucketlistSchema(many=True)

bucketlistitem_schema = BucketlistItemSchema()
bucketlistitems_schema = BucketlistItemSchema(many=True)


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
        - description (optional): A string representing the
                                    bucketlist's description
        - created_by (required): An foreign key from table User
                                    representing owner of bucketlist
        """

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if not isinstance(g.current_user, int):
            return g.current_user

        try:
            args = self.reqparse.parse_args()
            _bucketlist = args['bucketlist'].strip()
            _description = args['description']

            bucketlists = Bucketlist.query.filter(
                Bucketlist.created_by == g.current_user,
                Bucketlist.list_name.ilike(_bucketlist)).first()

            # Validate the bucketlist name
            if not _bucketlist:
                return {'Error': 'Bucketlist name is required'}, 400

            if _bucketlist.isdigit() or \
                    len(_bucketlist) < 5 \
                    or len(_bucketlist) > 20:

                return {
                    'Error': 'Invalid bucketlist name (5-20 characters)'
                }, 400

            if bucketlists:
                return {'Error': 'Bucketlist already exists'}, 409

            if _description:
                _description = _description.capitalize().strip()

            bucketlist = Bucketlist(list_name=_bucketlist.capitalize(),
                                    description=_description,
                                    created_by=g.current_user,
                                    )

            # Persist to DB
            db.session.add(bucketlist)
            db.session.commit()

            return {
                'Message': 'Bucketlist added successfully successfully'
            }, 201

        except Exception as error:
            db.rollback()
            return {'Error': str(error)}, 400

    def get(self):
        """
        Returns a list of all bucketlists for a particular user
        """

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if not isinstance(g.current_user, int):
            return g.current_user

        bucketlists = Bucketlist.query.filter_by(
            created_by=g.current_user).all()

        if not bucketlists:
            return {
                'Warning': 'No bucketlists available for current user'
            }, 400

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'q',
            type=str,
            location='args',
            help='Search bucketlist name'
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
            _query = _query.strip()

            bucketlists = Bucketlist.query.filter(
                Bucketlist.created_by == g.current_user,
                Bucketlist.list_name.ilike('%' + _query + '%')
            ).order_by(
                Bucketlist.list_id
            ).paginate(_page,
                       _limit,
                       False)

            if not bucketlists.items:
                return {
                    'Error': 'No bucketlists with the word {}'.format(_query)
                }, 404

        else:
            bucketlists = Bucketlist.query.filter(
                Bucketlist.created_by == g.current_user
            ).order_by(
                Bucketlist.list_id
            ).paginate(_page,
                       _limit,
                       False)

            if not bucketlists.items:
                return {
                    'Error': 'No bucketlists available for current user'
                }, 404

        if bucketlists.has_prev:
            prev_page = request.url_root + 'bucketlist_api/v1.0/bucketlists' \
                + '?page=' + str(_page - 1) + '&limit=' + str(_limit)
        else:
            prev_page = 'None'

        if bucketlists.has_next:
            next_page = request.url_root + 'bucketlist_api/v1.0/bucketlists' \
                + '?page=' + str(_page + 1) + '&limit=' + str(_limit)
        else:
            next_page = 'None'

        result = bucketlists_schema.dump(list(bucketlists.items))
        pages = {
            'message': {
                'prev_page': prev_page,
                'next_page': next_page,
                'total_pages': bucketlists.pages
            },
            'bucketlists': result.data
        }

        response = json.dumps(pages, sort_keys=False)

        return Response(
            response,
            status=200,
            mimetype='text/json'
        )


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
        return {
            'Error': 'Method not allowed. Use /bucketlist_api/v1.0/bucketlists'
        }, 405

    def get(self, id):

        # Validate token
        _token = request.headers.get("Authorization")
        g.current_user = verify_auth_token(_token)

        if not isinstance(g.current_user, int):
            return g.current_user

        # Validate user to perform CRUD action on a bucketlist
        bucketlist = Bucketlist.query.filter_by(
            list_id=id).first()

        # Check if bucketlist exists
        if not bucketlist:
            return {'Error': 'Bucketlist does not exist'}, 404

        if g.current_user != bucketlist.created_by:
            return {'Error': 'Unauthorised access'}, 401

        try:
            items = Bucketlist_Item.query.join(
                Bucketlist,
                (
                    Bucketlist_Item.list_id == Bucketlist.list_id)
            ).filter(Bucketlist.list_id == id).all()

            bucketlist_details = {
                'id': bucketlist.list_id,
                'name': bucketlist.list_name,
                'description': bucketlist.description,
                'items': ['No bucketlist items available'],
                'date_created': str(bucketlist.created_on),
                'date_modified': str(bucketlist.date_modified),
                'created_by': bucketlist.created_by,
                'done': bucketlist.is_completed,
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

            response = json.dumps(bucketlist_details, sort_keys=False)

            return Response(
                response,
                status=200,
                mimetype='text/json'
            )

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
                _bucketlist = _bucketlist.strip()

                if _bucketlist.isdigit() or \
                        len(_bucketlist) < 5 or \
                        len(_bucketlist) > 20:
                    return {
                        'Error': 'Invalid bucketlist name (5-20 characters)'
                    }, 400

                bucketlist = Bucketlist.query.filter(
                    Bucketlist.created_by == g.current_user,
                    Bucketlist.list_name.ilike(_bucketlist)).first()

                # Before updating, check if the bucketlist exists
                if bucketlist:
                    return {'Error': 'Bucketlist already exists'}, 400

                bucketlists.list_name = _bucketlist.capitalize()

            if _description:
                bucketlists.description = _description.capitalize().strip()

            if _done is not None and bool(_done):
                _done = _done.strip()
                # Check if bucketlist items are all done
                incomplete_items = Bucketlist_Item.query.filter(
                    Bucketlist_Item.list_id == id,
                    Bucketlist.is_completed.is_(False)).first()

                if incomplete_items:
                    return {
                        'Error': 'Bucketlist has incomplete items/activities'
                    }, 403

            bucketlists.is_completed = bool(_done)

            # Update date_modified
            bucketlists.date_modified = datetime.now().isoformat(
                sep=' ',
                timespec='minutes')

            # Commit changes
            db.session.commit()

            # Fetch updated record
            bucketlists = Bucketlist.query.filter_by(
                list_id=id).first()

            response = bucketlist_schema.jsonify(bucketlists)
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

        # Validate user to perform CRUD action on a bucketlist
        bucketlist = Bucketlist.query.filter_by(
            list_id=id).first()

        # Check if bucketlist exists
        if not bucketlist:
            return {'Error': 'Bucketlist does not exist'}, 404

        if g.current_user != bucketlist.created_by:
            return {'Error': 'Unauthorised access'}, 401

        try:
            # Delete bucketlist items for bucketlist
            db.session.query(Bucketlist_Item).filter(
                Bucketlist_Item.list_id == id).delete()

            db.session.delete(bucketlist)
            db.session.commit()
            return {'Message': 'Bucketlist deleted successfully'}, 200

        except Exception as error:
            db.session.rollback()
            return {'Error': str(error)}, 400


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
        items = Bucketlist_Item.query.filter_by(
            list_id=bucketlist_id,
            item_id=bucketlistitem_id
        ).first()

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
        - item_name (required): A string representing the bucketlist item name
        - description (optional): A string representing the
                                    bucketlist item's description
        - list_id (required): A foreign key from table Bucketlist
                                representing bucketlist id
        """

        # Validate user to perform CRUD action on a bucketlist
        current_user = validate_access(self, id)

        if isinstance(current_user, (tuple, set)):
            return current_user

        args = self.reqparse.parse_args()
        _item = args['item'].strip()
        _description = args['description']

        items = Bucketlist_Item.query.filter(
            Bucketlist_Item.list_id == id,
            Bucketlist_Item.item_name.ilike(_item)).first()

        if not _item:
            return {'Error': 'Bucketlist item name is required'}, 400

        if _item.isdigit() or len(_item) < 5 or len(_item) > 20:
            return {
                'Error': 'Invalid bucketlist name or length (5-20 characters)'
            }, 400

        if items:
            return {'Error': 'Bucketlist item already exists'}, 400

        # Check if bucketlist exists
        items = Bucketlist.query.filter(
            Bucketlist.list_id == id).first()

        if not items:
            return {'Error': 'Bucketlist does not exists'}, 400

        if _description:
            _description = _description.capitalize().strip(),

        try:

            item = Bucketlist_Item(item_name=_item,
                                   description=_description,
                                   list_id=id,
                                   )

            # Persist to DB
            db.session.add(item)
            db.session.commit()

            return {
                'Message': 'Bucketlist item added successfully successfully'
            }, 201

        except Exception as error:
            db.rollback()
            return {'Error': str(error)}, 400

    def get(self, id):
        """
        Method not allowed for single bucketlist item
        """

        return {
            'Error': 'Not allowed. Use /bucketlist_api/v1.0/bucketlists/<id>'
        }, 405


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
                                   help='Is the bucketlist item completed?')

        super(SingleBucketlistItemAPI, self).__init__()

    def post(self, id, item_id):
        return {
            'Error': 'Use /bucketlist_api/v1.0/bucketlists/<id>/items'
        }, 405

    def get(self, id, item_id):

        # Validate user access
        current_user = validate_access(self, id, item_id)

        if not str(current_user).isdigit():
            return current_user

        items = Bucketlist_Item.query.filter_by(list_id=id,
                                                item_id=item_id).first()

        try:

            response = bucketlistitem_schema.jsonify(items)
            response.status_code = 200
            return response

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

        items = Bucketlist_Item.query.filter(
            Bucketlist_Item.item_id == item_id,
            Bucketlist_Item.list_id == id
        ).first()

        if _item:
            _item = _item.strip()
            if _item.isdigit() or len(_item) < 5 or len(_item) > 20:
                return {
                    'Error': 'Invalid bucketlist name (5-20 characters)'
                }, 400

            item = Bucketlist_Item.query.filter(
                Bucketlist_Item.list_id == id,
                Bucketlist_Item.item_name.ilike(_item)
            ).first()

            # Before updating, check if the bucketlist exists
            if item:
                return {'Error': 'Bucketlist item already exists'}, 400

            items.item_name = _item

        if _description:
            _description = _description.strip()
            items.description = _description

        if _done:
            items.is_completed = bool(_done)

        # Update date_modified
        items.date_modified = datetime.now().isoformat(
            sep=' ',
            timespec='minutes')

        try:

            # Commit changes
            db.session.commit()

            # Fetch updated record
            items = Bucketlist_Item.query.filter_by(
                item_id=item_id).first()

            response = bucketlistitem_schema.jsonify(items)
            response.status_code = 200
            return response

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
