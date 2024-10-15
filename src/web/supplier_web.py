from logging import getLogger
from flask_restx import Resource, Namespace, ValidationError
from sqlalchemy.exc import NoResultFound

from src.handlers.supplier_handler import SupplierHandler
from src.models.supplier import SupplierSchema
from marshmallow_jsonschema import JSONSchema
from flask import request

from src.web.schema import SupplierPutArgsSchema

logger = getLogger(__name__)

supplier_api = Namespace('suppliers', description='Supplier related operations')

supplier_handler = SupplierHandler()

from flask_jwt_extended import jwt_required, current_user

supplier_get_schema = SupplierSchema()
supplier_get_model = supplier_api.schema_model(
    'SupplierGetModel', JSONSchema().dump(supplier_get_schema)['definitions']['SupplierSchema'])

supplier_post_schema = SupplierSchema(exclude=['id', 'created_at', 'updated_at'])
supplier_post_model = supplier_api.schema_model(
    'SupplierPostModel', JSONSchema().dump(supplier_post_schema)['definitions']['SupplierSchema']
)

supplier_put_args_schema = SupplierPutArgsSchema()
supplier_put_args_model = supplier_api.schema_model(
    'SupplierPutArgsModel',
    JSONSchema().dump(supplier_put_args_schema)['definitions']['SupplierPutArgsSchema']
)


@supplier_api.route('')
class SupplierCollectionWeb(Resource):

    @jwt_required()
    @supplier_api.response(200, 'Supplier created successfully', [supplier_get_model])
    @supplier_api.response(403, 'Forbidden')
    @supplier_api.response(500, 'Internal Server Error')
    def get(self):
        if current_user.role_id != 1 and current_user.role_id != 6:
            return {'message': 'You are not authorized to access this resource'}, 403
        return supplier_get_schema.dump(supplier_handler.get_suppliers(), many=True), 200

    @jwt_required()
    @supplier_api.expect(supplier_post_model)
    @supplier_api.response(201, 'Success', supplier_get_model)
    @supplier_api.response(400, 'Invalid data input')
    @supplier_api.response(403, 'Forbidden')
    @supplier_api.response(500, 'Internal Server Error')
    def post(self):
        if current_user.role_id != 1 and current_user.role_id != 6:
            return {'message': 'You are not authorized to access this resource'}, 403
        try:
            data = supplier_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400
        try:
            new_supplier = supplier_handler.add_supplier(**data)
            logger.info(f'New supplier {new_supplier}')
            return supplier_get_schema.dump(new_supplier), 201
        except Exception as e:
            return {'error': str(e)}, 500


@supplier_api.route('/<int:supplier_id>')
class SupplierWeb(Resource):

    @jwt_required()
    @supplier_api.response(200, 'Success', supplier_get_model)
    @supplier_api.response(403, 'Forbidden')
    @supplier_api.response(404, 'Supplier not found')
    @supplier_api.response(500, 'Internal Server Error')
    def get(self, supplier_id):
        supplier = supplier_handler.get_supplier_by_id(supplier_id)
        if supplier is None:
            return {'message': 'Supplier not found'}, 404
        return supplier_get_schema.dump(supplier), 200

    @jwt_required()
    @supplier_api.response(204, 'Supplier deleted successfully')
    @supplier_api.response(403, 'Fprbidden')
    @supplier_api.response(500, 'Internal Server Error')
    def delete(self, supplier_id):
        if current_user.role_id != 1 and current_user.role_id != 6:
            return {'message': 'You are not authorized to access this resource'}, 403
        supplier_handler.delete_supplier(supplier_id)
        return {'message': 'Supplier deleted'}, 204

    @jwt_required()
    @supplier_api.expect(supplier_put_args_model)
    @supplier_api.response(200, 'Supplier updated successfully', supplier_get_model)
    @supplier_api.response(400, 'Invalid data input')
    @supplier_api.response(404, 'Not Found')
    @supplier_api.response(500, 'Internal Server Error')
    def put(cls, supplier_id):
        try:
            data = supplier_put_args_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400

        try:
            supplier = supplier_handler.update_supplier(supplier_id, **data)
            return supplier_get_schema.dump(supplier), 200
        except NoResultFound as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


