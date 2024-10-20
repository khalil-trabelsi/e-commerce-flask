from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace, ValidationError
from marshmallow_jsonschema import JSONSchema
from flask import request
from logging import getLogger

from src.handlers.collection_handler import CollectionHandler
from src.models.collection import CollectionSchema
from src.web.schema import CategoryPostArgsSchema, CategoryPutArgsSchema

collection_api = Namespace('collections', description='Collections related operations')

collection_get_schema = CollectionSchema()
collection_get_model = collection_api.schema_model(
    'CollectionGetModel', JSONSchema().dump(collection_get_schema)['definitions']['CollectionSchema']
)

collection_post_schema = CollectionSchema(only=('name', 'description'))
collection_post_model = collection_api.schema_model(
    'CollectionPostModel', JSONSchema().dump(collection_post_schema)['definitions']['CollectionSchema']
)


@collection_api.route('')
class CategoryCollectionWeb(Resource):
    @collection_api.response(200, 'Success', [collection_get_model])
    @collection_api.response(500, 'Internal Server Error')
    def get(self):
        collections = CollectionHandler.get_collections()
        return collection_get_schema.dump(collections, many=True), 200

    @collection_api.response(200, 'Success', collection_get_model)
    @collection_api.response(400, 'Invalid Input Data')
    @collection_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = collection_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400
        try:
            created_collection = CollectionHandler.add_collection(**data)
            return collection_get_schema.dump(created_collection), 201
        except Exception as err:
            return {'error': str(err)}, 500




