from logging import getLogger
from flask_restx import Resource, Namespace, marshal, ValidationError
from marshmallow_jsonschema import JSONSchema

from src.handlers.auth_handler import AuthHandler
from src.handlers.user_handler import UserHandler


from flask_jwt_extended import jwt_required, current_user
from flask import request, make_response, jsonify
from src.models.user import UserSchema
from src.web.schema import UserPostArgsSchema, UserPutArgsSchema

logger = getLogger(__name__)


user_api = Namespace('users', description='User related operations')

user_get_schema = UserSchema(exclude=['password', 'token', 'updated_at'], many=True)
user_get_model = user_api.schema_model(
    'userGetModel', JSONSchema().dump(user_get_schema)['definitions']['UserSchema']
)

user_post_schema = UserPostArgsSchema()
user_post_model = user_api.schema_model(
    'userPostArgsModel', JSONSchema().dump(user_post_schema)['definitions']['UserPostArgsSchema']
)

user_put_schema = UserPutArgsSchema()
user_put_model = user_api.schema_model(
    'userPutArgsModel', JSONSchema().dump(user_put_schema)['definitions']['UserPutArgsSchema']
)


@user_api.route('')
class UserCollectionWeb(Resource):

    @jwt_required()
    @user_api.response(200, 'Success', [user_get_model] )
    @user_api.response(403, 'Forbidden')
    @user_api.response(400, 'Invalid input data')
    @user_api.response(500, 'Internal server error')
    def get(self):
        if current_user.role_id != 1:
            return {'error': 'You are not authorized to access this resource!'}, 403
        users = UserHandler.get_users()
        return user_get_schema.dump(users), 200

    @jwt_required()
    @user_api.expect(user_post_model)
    @user_api.response(200, 'Success', user_get_model)
    @user_api.response(403, 'Forbidden')
    @user_api.response(400, 'Invalid input data')
    @user_api.response(500, 'Internal server error')
    def post(self):
        logger.info(user_get_model)
        try:
            data = user_post_schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Invalid input data'}, 400
        try:
            user = AuthHandler.register(**data)
        except ValueError as err:
            return str(err), 409
        except Exception as err:
            return str(err), 500

        return user_get_schema.dump(user), 201


@user_api.route('/<int:user_id>')
class UserWeb(Resource):

    @jwt_required()
    @user_api.response(200, 'Success', user_get_model )
    @user_api.response(401, 'Unauthorized')
    def get(self, user_id):
        user = UserHandler.get_user_by_id(user_id)
        return user_get_schema.dump(user), 200

    @jwt_required()
    @user_api.response(200, 'Success')
    @user_api.response(403, 'Forbidden')
    def delete(self, user_id: int):
        deleted_user_id = UserHandler.delete_user(user_id)
        return {'deleted_user_id': deleted_user_id}, 200

    @jwt_required()
    @user_api.expect(user_put_model)
    @user_api.response(200, 'Success')
    @user_api.response(403, 'Forbidden')
    @user_api.response(400, 'Invalid input data')
    @user_api.response(500, 'Internal server error')
    def put(self, user_id: int):
        try:
            data = user_put_schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Invalid input data'}, 400
        try:
            updated_user_id = UserHandler.edit_user(user_id, data)
        except Exception as err:
            return str(err), 500

        return updated_user_id, 200


