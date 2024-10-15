import base64
import os.path
from logging import getLogger
from flask import request,send_file,jsonify
from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace,ValidationError
from werkzeug.datastructures import FileStorage


from src.handlers.product_handler import ProductHandler
from src.models.product import ProductSchema
from marshmallow_jsonschema import JSONSchema

from src.models.product_images import ProductImagesSchema
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

product_post_schema = ProductSchema(only=('name', 'price_ht', 'tva', 'brand_id', 'category_id'))
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


@product_api.route('')
class ProductCollectionWeb(Resource):
    @jwt_required()
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
    @jwt_required()
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
            paths = ProductHandler.add_product_images(product_id, files)
            logger.info(paths)
            return paths, 201
        except Exception as e:
            return {'error': str(e)}, 500


@product_api.route('/images/<string:filename>')
class ServeImage(Resource):
    @jwt_required()
    @product_api.response(200, 'Success')
    def get(self, filename):
        file_path = os.path.join(get_upload_folder(), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=False)
        else:
            return jsonify({'error': 'File not found'}), 404
