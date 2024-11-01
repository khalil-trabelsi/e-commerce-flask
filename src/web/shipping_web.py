from flask import request
from flask_restx import Namespace, Resource, ValidationError
from marshmallow_jsonschema import JSONSchema

from src.models.shipping_address import ShippingAddressSchema
from src.handlers.shipping_handler import ShippingHandler

shipping_api = Namespace('shipping', description='Shipping related operations')

shipping_get_schema = ShippingAddressSchema()
shipping_get_model = shipping_api.schema_model(
    'ShippingAddressGetModel', JSONSchema().dump(shipping_get_schema)['definitions']['ShippingAddressSchema']
)

shipping_post_schema = ShippingAddressSchema(only=('street', 'city', 'country', 'customer_id', 'postal'))
shipping_post_model = shipping_api.schema_model(
    'ShippingAddressPostModel', JSONSchema().dump(shipping_post_schema)['definitions']['ShippingAddressSchema']
)


@shipping_api.route('')
class ShippingAddress(Resource):
    @shipping_api.response(200, 'Success', [shipping_get_model])
    @shipping_api.response(500, 'Internal Server Error')
    def get(self):
        shipping_address = ShippingHandler.get_shipping_addresses()
        return shipping_get_schema.dump(shipping_address, many=True), 200

    @shipping_api.response(201, 'Success', shipping_get_model)
    @shipping_api.response(400, 'Invalid Input Data')
    @shipping_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = shipping_post_schema.load(request.json)
        except ValidationError as err:
            return str(err), 400

        try:
            shipping_address = ShippingHandler.add_shipping_address(**data)
            return shipping_get_schema.dump(shipping_address), 201

        except Exception as err:
            return str(err), 500