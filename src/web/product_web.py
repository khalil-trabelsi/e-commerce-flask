import os.path
from logging import getLogger
from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace,ValidationError
from werkzeug.datastructures import FileStorage


from src.handlers.product_handler import ProductHandler
from src.models.product import ProductSchema
from marshmallow_jsonschema import JSONSchema

from src.models.product_images import ProductImagesSchema
from src.models.product_review import ProductReviewSchema
from src.web.schema import ProductImagePostArgsSchema
from src.helpers.FileConf import get_upload_folder

product_api = Namespace('products', description='Product related operations')
product_handler = ProductHandler()

product_image_schema = ProductImagesSchema()
product_image_model = product_api.schema_model(
    'ProductImagesModel', JSONSchema().dump(product_image_schema)['definitions']['ProductImagesSchema']
)


product_get_schema = ProductSchema()
product_get_model = product_api.schema_model(
    'ProductGetModel', JSONSchema().dump(product_get_schema)['definitions']['ProductSchema']
)

product_post_schema = ProductSchema(only=('name', 'price_ht', 'tva', 'brand_id', 'category_id', 'collection_id', 'features'))
product_post_model = product_api.schema_model(
    'ProductPostModel', JSONSchema().dump(product_post_schema)['definitions']['ProductSchema']
)

logger = getLogger(__name__)


product_images_post_schema = ProductImagePostArgsSchema()

product_images_post_model = product_api.schema_model(
    'ProductImagePostModel', JSONSchema().dump(product_images_post_schema)['definitions']['ProductImagePostArgsSchema']
)


upload_parser = product_api.parser()
upload_parser.add_argument('files', location='files', type=FileStorage, required=True, action='append', help='Fichiers à uploader')
upload_parser.add_argument('main_image', type=str, required=True)

product_review_post_schema = ProductReviewSchema(only=('title', 'comment', 'rating', 'user_id', 'username'))
product_review_post_model = product_api.schema_model(
    'ProductReviewModel', JSONSchema().dump(product_review_post_schema)['definitions']['ProductReviewSchema']
)


product_review_get_schema = ProductReviewSchema()
product_review_get_model = product_api.schema_model(
    'ProductReviewGetModel', JSONSchema().dump(product_review_post_schema)['definitions']['ProductReviewSchema']
)


@product_api.route('')
class ProductCollectionWeb(Resource):
    @product_api.response(200, 'Success', [product_get_model])
    @product_api.response(500, 'Internal Server Error')
    def get(self):
        logger.info(product_get_model)
        try:
            products = product_handler.get_all_products()
            return product_get_schema.dump(products, many=True), 200
        except Exception as e:
            return {'error': str(e)}, 500
    @jwt_required()
    @product_api.expect(product_post_model)
    @product_api.response(201, 'Success', product_get_model)
    @product_api.response(400, 'Invalid input data')
    @product_api.response(409, 'Product already exists')
    @product_api.response(500, 'Success', )
    def post(self):
        try:
            data = product_post_schema.load(request.json)
            logger.info(data)
        except ValidationError as e:
            return {'error': str(e)}, 400
        try:
            product = product_handler.add_product(**data)
            return product_get_schema.dump(product), 201
        except ValueError as e:
            return {'error': str(e)}, 409
        except Exception as e:
            return {'error': str(e)}, 500


@product_api.route('/<int:product_id>')
class ProductWeb(Resource):
    @product_api.response(200, 'Success', product_get_model)
    @product_api.response(500, 'Internal Server Error')
    def get(self, product_id):
        product = ProductHandler.get_product_by_id(product_id)
        return product_get_schema.dump(product), 200


@product_api.route('/<int:product_id>/upload')
class ProductUploadWeb(Resource):
    @jwt_required()
    @product_api.expect(upload_parser)
    @product_api.response(201, 'Success')
    def post(self, product_id: int):
        try:
            files = request.files.getlist('files')
            main_image = request.values.get('main_image')
            paths = ProductHandler.add_product_images(product_id, files, main_image)
            logger.info(paths)
            return paths, 201
        except Exception as e:
            return {'error': str(e)}, 500


@product_api.route('/<int:product_id>/review')
class ProductReviewWeb(Resource):

    @product_api.response(200, 'Success', [product_get_model])
    @product_api.response(500, 'Internal Server Error')
    def get(self, product_id):
        product_reviews = ProductHandler.get_product_review(product_id)
        return product_review_get_schema.dump(product_reviews, many=True), 200

    @product_api.response(200, 'Success', product_review_post_model)
    def post(self, product_id: int):
        try:
            data = product_review_post_schema.load(request.json)
        except ValidationError as e:
            return {'error': str(e)}, 400

        product_review = ProductHandler.add_product_review(product_id=product_id, **data)

        return  product_review_post_schema.dump(product_review), 200

