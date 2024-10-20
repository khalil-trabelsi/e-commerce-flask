from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace, ValidationError
from marshmallow_jsonschema import JSONSchema
from flask import request
from logging import getLogger

from src.handlers.category_handler import CategoryHandler
from src.models.category import CategorySchema
from src.web.schema import CategoryPostArgsSchema, CategoryPutArgsSchema

category_api = Namespace('categories', description='Categories related operations')

category_handler = CategoryHandler()

category_get_schema = CategorySchema(exclude=['parent', 'children'])
category_get_model = category_api.schema_model(
    'CategoryGetModel', JSONSchema().dump(category_get_schema)['definitions']['CategorySchema']
)

category_aggregated_get_schema = CategorySchema()
category_aggregated_get_model = category_api.schema_model(
    'CategoryAggregatedGetModel', JSONSchema().dump(category_aggregated_get_schema)['definitions']['CategorySchema']
)

category_post_schema = CategoryPostArgsSchema()
category_post_model = category_api.schema_model(
    'CategoryPostModel', JSONSchema().dump(category_post_schema)['definitions']['CategoryPostArgsSchema']
)

category_put_schema = CategoryPutArgsSchema()
category_put_model = category_api.schema_model(
    'CategoryPutModel', JSONSchema().dump(category_put_schema)['definitions']['CategoryPutArgsSchema']
)


@category_api.route('')
class CategoryCollectionWeb(Resource):
    @category_api.response(200, 'Success', [category_get_model])
    @category_api.response(500, 'Internal Server Error')
    def get(self):
        categories = category_handler.get_all_categories()
        return category_get_schema.dump(categories, many=True), 200

    @jwt_required()
    @category_api.expect(category_post_model)
    @category_api.response(200, 'Success', category_get_model)
    @category_api.response(400, 'Invalid Input Data')
    @category_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = category_post_schema.load(request.json)
        except ValidationError as err:
            return {"error": str(err)}, 400
        try:
            category = category_handler.add_category(**data)
            return category_get_schema.dump(category), 201
        except Exception as err:
            return {"error": str(err)}, 500


@category_api.route('/aggregated')
class CategoryAggregatedWeb(Resource):
    @jwt_required()
    @category_api.response(200, 'Success', [category_aggregated_get_model])
    @category_api.response(500, 'Internal Server Error')
    def get(self):
        categories = category_handler.get_all_categories()
        return category_aggregated_get_schema.dump(categories, many=True), 200


@category_api.route('/<int:category_id>')
class CategoryWeb(Resource):
    @category_api.response(200, 'Success', category_get_model)
    @category_api.response(404, 'Category not found', category_get_model)
    @category_api.response(500, 'Internal Server Error', category_get_model)
    def get(self, category_id):
        return category_handler.get_category_by_id(category_id)

    @jwt_required()
    @category_api.response(200, 'Success', category_get_model)
    @category_api.response(404, 'Category not found')
    @category_api.response(500, 'Internal Server Error')
    def delete(self, category_id):
        category_handler.delete_category(category_id)

        return {'message': f'Category {category_id} deleted'}

    @jwt_required()
    @category_api.response(200, 'Success', int)
    @category_api.response(400, 'Invalid data input')
    @category_api.response(500, 'Internal Server Error')
    def put(self, category_id):
        try:
            data = category_put_schema.load(request.json)
        except ValidationError as err:
            return {"error": str(err)}, 400

        try:
            category_handler.update_category(category_id, **data)
            return category_id, 200

        except Exception as err:
            return {"error": str(err)}, 500


