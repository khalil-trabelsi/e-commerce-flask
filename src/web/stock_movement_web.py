from logging import getLogger
from flask import request
from flask_restx import Resource, Namespace,ValidationError
from marshmallow_jsonschema import JSONSchema
from flask_jwt_extended import jwt_required, current_user

from src.models.stock_movement import StockMovementSchema
from src.handlers.stock_movement_handler import StockMovementHandler

from .schema import StockMovementFilterArgsSchema

logger = getLogger(__name__)

stock_movement_api = Namespace('stock_movements', description='Stock movements related operations')

stock_movement_handler = StockMovementHandler()

stock_movement_get_schema = StockMovementSchema()
stock_movement_get_model = stock_movement_api.schema_model(
    'StockMovementModel',
    JSONSchema().dump(stock_movement_get_schema)['definitions']['StockMovementSchema']
)

stock_movement_post_schema = StockMovementSchema(only=['product_id', 'supplier_id', 'reference', 'movement_type', 'quantity'])
stock_movement_post_model = stock_movement_api.schema_model(
    'StockMovementModel', JSONSchema().dump(stock_movement_post_schema)['definitions']['StockMovementSchema']
)

stock_movement_filter_args_schema = StockMovementFilterArgsSchema()
stock_movement_filter_args_model = stock_movement_api.schema_model(
    'StockMovementFilterArgsModel', JSONSchema().dump(stock_movement_filter_args_schema)['definitions']['StockMovementFilterArgsSchema']
)


@stock_movement_api.route('')
class StockMovementCollectionWeb(Resource):

    @stock_movement_api.response(200, 'Success', [stock_movement_get_model])
    @stock_movement_api.response(500, 'Internal Server Error')
    def get(self):
        suppliers_id = request.args.getlist('supplier_id', type=int)
        products_id = request.args.getlist('product_id', type=int)
        min_quantity = request.args.get('min_quantity', type=int)
        max_quantity = request.args.get('max_quantity', type=int)
        try:
            stock_movements = stock_movement_handler.get_stock_movements(suppliers_id, products_id, min_quantity, max_quantity)
            return stock_movement_get_schema.dump(stock_movements, many=True), 200
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @stock_movement_api.expect(stock_movement_post_model)
    @stock_movement_api.response(200, 'Success', stock_movement_get_model)
    @stock_movement_api.response(400, 'Invalid input data')
    @stock_movement_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = stock_movement_post_schema.load(request.json)
        except ValidationError as e:
            return {'error': str(e)}, 400

        try:
            stock_movement = stock_movement_handler.add_stock_movement(**data, user_id=current_user.id)
            return stock_movement_get_schema.dump(stock_movement), 201
        except Exception as e:
            return {'error': str(e)}, 500


