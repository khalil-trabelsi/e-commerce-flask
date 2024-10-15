from logging import getLogger
from flask_restx import Resource, Namespace, marshal, ValidationError
from marshmallow_jsonschema import JSONSchema
from flask_jwt_extended import jwt_required, current_user
from flask import request, make_response, jsonify

from src.handlers.auth_handler import AuthHandler
from src.handlers.user_handler import UserHandler


from src.models.user import UserSchema, RoleSchema
from src.web.schema import AdminPostArgsSchema, UserPutArgsSchema, UserGetSchema

logger = getLogger(__name__)


admin_api = Namespace('administrators', description='Admin related operations')

user_get_schema = UserGetSchema(exclude=['password', 'token'])
user_get_model = admin_api.schema_model(
    'userGetModel', JSONSchema().dump(user_get_schema)['definitions']['UserGetSchema']
)

admin_post_schema = AdminPostArgsSchema()
admin_post_model = admin_api.schema_model(
    'adminPostArgsModel', JSONSchema().dump(admin_post_schema)['definitions']['AdminPostArgsSchema']
)

user_put_schema = UserPutArgsSchema()
user_put_model = admin_api.schema_model(
    'userPutArgsModel', JSONSchema().dump(user_put_schema)['definitions']['UserPutArgsSchema']
)


@admin_api.route('')
class AdminCollectionWeb(Resource):

    @jwt_required()
    @admin_api.response(200, 'Success', [user_get_model])
    @admin_api.response(403, 'Forbidden')
    @admin_api.response(400, 'Invalid input data')
    @admin_api.response(500, 'Internal server error')
    def get(self):
        if current_user.role_id != 1:
            return {'error': 'You are not authorized to access this resource!'}, 403
        users = UserHandler.get_admins()
        return user_get_schema.dump(users, many=True), 200

    @jwt_required()
    @admin_api.expect(admin_post_model)
    @admin_api.response(200, 'Success', user_get_model)
    @admin_api.response(403, 'Forbidden')
    @admin_api.response(400, 'Invalid input data')
    @admin_api.response(500, 'Internal server error')
    def post(self):
        logger.info(user_get_model)
        try:
            data = admin_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Invalid input data'}, 400
        try:
            user = AuthHandler.register(**data)
        except ValueError as err:
            return {'message': str(err)}, 409
        except Exception as err:
            return {'error': str(err)}, 500

        return user_get_schema.dump(user), 201


@admin_api.route('/<int:user_id>')
class AdminWeb(Resource):

    @jwt_required()
    @admin_api.response(200, 'Success', user_get_model )
    @admin_api.response(401, 'Unauthorized')
    def get(self, user_id):
        user = UserHandler.get_user_by_id(user_id)
        return user_get_schema.dump(user), 200

    @jwt_required()
    @admin_api.response(200, 'Success')
    @admin_api.response(403, 'Forbidden')
    def delete(self, user_id: int):
        deleted_user_id = UserHandler.delete_user(user_id)
        return {'deleted_user_id': deleted_user_id}, 200

    @jwt_required()
    @admin_api.expect(user_put_model)
    @admin_api.response(200, 'Success')
    @admin_api.response(403, 'Forbidden')
    @admin_api.response(400, 'Invalid input data')
    @admin_api.response(500, 'Internal server error')
    def put(self, user_id: int):
        try:
            data = user_put_schema.load(request.json)
        except ValidationError as err:
            return {'error': str(err)}, 400
        try:
            updated_user_id = UserHandler.edit_user(user_id, **data)
        except Exception as err:
            return str(err), 500

        return updated_user_id, 200

