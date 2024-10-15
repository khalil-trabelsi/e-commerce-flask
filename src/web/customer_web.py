from flask_jwt_extended import jwt_required
from flask_restx import Resource, Namespace, ValidationError
from flask import request
from logging import getLogger
from marshmallow_jsonschema import JSONSchema

from src.handlers.user_handler import UserHandler
from src.handlers.auth_handler import AuthHandler
from .admin_web import (
    user_get_schema,
    user_put_schema,
    user_get_model,
    user_put_model,
)
from ..models.customer import CustomerSchema

from .schema import CustomerPostArgsSchema

logger = getLogger(__name__)

customer_api = Namespace('customers', description='Customers related operations')

customer_get_schema = CustomerSchema()
customer_get_model = customer_api.schema_model(
    'CustomerGetModel', JSONSchema().dump(customer_get_schema)['definitions']['CustomerSchema']
)

customer_post_schema = CustomerPostArgsSchema()
customer_post_model = customer_api.schema_model(
    'CustomerPostModel', JSONSchema().dump(customer_post_schema)['definitions']['CustomerPostArgsSchema']
)

@customer_api.route('')
class CustomerCollectionWeb(Resource):
    @jwt_required()
    @customer_api.response(200, 'Success', [customer_get_model])
    @customer_api.response(500, 'Internal Server Error')
    def get(self):
        try:
            customers = UserHandler.get_customers()
            return customer_get_schema.dump(customers, many=True), 200
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @customer_api.expect(customer_post_model)
    @customer_api.response(200, 'Success', user_get_model)
    @customer_api.response(403, 'Forbidden')
    @customer_api.response(400, 'Invalid input data')
    @customer_api.response(500, 'Internal server error')
    def post(self):
        try:
            data = customer_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': f'Invalid input data {str(err)}'}, 400
        logger.info(request.json)
        try:
            user = AuthHandler.register(**data)
        except ValueError as err:
            return {'message': str(err)}, 409
        except Exception as err:
            return {'error': str(err)}, 500
        return user_get_schema.dump(user), 201


@customer_api.route('/<int:customer_id>')
class CustomerWeb(Resource):
    @jwt_required()
    @customer_api.response(200, 'Success', user_get_model)
    @customer_api.response(500, 'Internal Server Error')
    def get(self, customer_id):
        try:
            customer = UserHandler.get_user_by_id(customer_id)
            return user_get_schema.dump(customer), 200
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @customer_api.expect(user_put_model)
    @customer_api.response(200, 'Success', user_get_model)
    @customer_api.response(400, 'Invalid input data')
    @customer_api.response(500, 'Internal Server Error')
    def put(self, customer_id):
        try:
            data = user_put_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400
        try:
            customer = UserHandler.edit_user(customer_id, **data)
            logger.info(customer)
            return user_get_schema.dump(customer), 200
        except Exception as err:
            return {'error': str(err)}, 500

