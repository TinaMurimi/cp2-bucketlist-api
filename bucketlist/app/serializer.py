from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from bucketlist.app.models import User, Bucketlist, Bucketlist_Item

# Insantiate an object from the Marshmallow serialization/ deserialization
# library
marshmallow = Marshmallow()


class UserSchema(marshmallow.ModelSchema):
    # bucketlists = marshmallow.Nested('BucketlistSchema', many=True)

    # _links = marshmallow.Hyperlinks({
    #     'self': marshmallow.URL('user', id='<id>'),
    #     'collection': marshmallow.URL('user')
    # })

    class Meta:
        # Fields to show
        fields = ('user_id', 'username', 'email', 'active', 'created_on')

        model = User
        ordered = True


class BucketlistSchema(marshmallow.ModelSchema):
    class Meta:
        # Fields to show
        fields = (
            'list_id',
            'list_name',
            'description',
            'created_on',
            'date_modified',
            # 'created_by',
            'is_completed',
        )

        model = Bucketlist
        ordered = True


class BucketlistDetailsSchema(marshmallow.ModelSchema):

    # items = marshmallow.Nested('BucketlistItemSchema', many=True)

    # _links = marshmallow.Hyperlinks({
    #     'self': marshmallow.URL('bucketlist', id='<id>'),
    #     'collection': marshmallow.URL('bucketlist')
    # })

    class Meta:
        # Fields to show
        fields = (
            'list_id',
            'list_name',
            'description',
            'items',
            'created_on',
            'date_modified',
            'created_by',
            'is_completed',
        )

        model = Bucketlist
        ordered = True


class BucketlistItemSchema(marshmallow.ModelSchema):
    class Meta:

        # Fields to show
        fields = ('item_id',
                  'list_id',
                  'item_name',
                  'description',
                  'created_on',
                  'date_modified',
                  'is_completed',
                  )

        model = Bucketlist_Item
        ordered = True
