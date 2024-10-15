from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace, ValidationError
from marshmallow_jsonschema import JSONSchema

from src.handlers.brand_handler import BrandHandler
from src.models.brand import BrandSchema

brand_api = Namespace('brands', description='Brands related operations')


brand_get_schema = BrandSchema()
brand_get_model = brand_api.schema_model(
    'BrandGetModel',
    JSONSchema().dump(brand_get_schema)['definitions']['BrandSchema']
)

brand_post_schema = BrandSchema(exclude=['id'])
brand_post_model = brand_api.schema_model(
    'BrandPostModel', JSONSchema().dump(brand_post_schema)['definitions']['BrandSchema']
)


@brand_api.route('')
class BrandCollectionWeb(Resource):
    @jwt_required()
    @brand_api.response(200, 'Success.', [brand_get_model])
    @brand_api.response(500, 'Success.')
    def get(self):
        try:
            brands = BrandHandler.get_all_brands()
            return brand_get_schema.dump(brands, many=True), 200
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @brand_api.expect(brand_post_schema)
    @brand_api.response(201, 'Success', brand_post_model)
    @brand_api.response(400, 'Invalid Input Data')
    @brand_api.response(201, 'Internal Server Error')
    def post(self):
        try:
            data = brand_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400

        try:
            brand = BrandHandler.add_brand(**data)
            return brand_get_schema.dump(brand), 201
        except Exception as e:
            return {'error': str(e)}, 500

