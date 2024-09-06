from logging import getLogger
from flask import request, make_response, jsonify
from flask_restx import Resource, ValidationError, Namespace
from marshmallow import fields

from src.handlers.auth_handler import AuthHandler
from marshmallow_jsonschema import JSONSchema
from src.models.user import UserSchema
from src.web.schema import LoginArgsSchema
from flask_jwt_extended import jwt_required, set_refresh_cookies


logger = getLogger(__name__)

auth_api = Namespace('auth', description='Authentication related operations')


user_post_schema = UserSchema(exclude=['id', 'created_at', 'updated_at', 'token'])
user_post_model = auth_api.schema_model(
    'userPostSchema', JSONSchema().dump(user_post_schema)['definitions']['UserSchema']
)

user_get_schema = UserSchema(exclude=[ 'updated_at', 'token', 'password'])
user_get_model = auth_api.schema_model(
    'userGetSchema', JSONSchema().dump(user_get_schema)['definitions']['UserSchema']
)

user_register_schema = UserSchema(exclude=['created_at', 'updated_at', 'token', 'role'])
user_register_model = auth_api.schema_model(
    'userGetSchema', JSONSchema().dump(user_get_schema)['definitions']['UserSchema']
)

login_args_schema = LoginArgsSchema()
login_args_model = auth_api.schema_model(
    'loginArgsSchema', JSONSchema().dump(login_args_schema)['definitions']['LoginArgsSchema']
)

# def schema_to_model(schema, name):
#     schema_dict = schema.dump(schema.Meta.model())
#     return auth_api.model(name, {
#         field: fields.Raw(example=value) for field, value in schema_dict.items()
#     })
#
# user_register_model = schema_to_model(user_register_schema, 'UserRegisterModel')

@auth_api.route("/register", methods=['POST'])
class Register(Resource):
    @auth_api.expect(user_register_model)
    @auth_api.response(201, 'User created Successfully', [user_register_model])
    @auth_api.response(409, 'Validation Error: Bad Request')
    @auth_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = user_register_schema.load(request.json)
        except ValidationError as err:
            return str(err.msg), 400
        try:
            created_user = AuthHandler.register(**data)
        except ValueError as err:
            return str(err), 409
        except Exception as err:
            logger.error(err)
            return {'error': str(err)}, 500
        return user_get_schema.dump(created_user), 201


@auth_api.route("/login", methods=['POST'])
class Login(Resource):
    @auth_api.expect(login_args_model)
    @auth_api.response(200, 'User logged Successfully')
    @auth_api.response(409, 'Validation Error: Bad Request')
    @auth_api.response(401, 'Invalid credentials')
    @auth_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = login_args_schema.load(request.json)
        except ValidationError as err:
            return str(err.msg), 409
        try:
            result = AuthHandler.login(**data)
            resp = make_response(jsonify({'user': user_get_schema.dump(result['user']), 'token': result['token']}), 200)
            resp.set_cookie(
                'refresh_token_cookie',
                value=result['refresh_token'],
                httponly=True,
                max_age=60*60*24*30,
                samesite='None',
                secure=True,
                path='/',
            )
            # set_refresh_cookies(resp, result['refresh_token'])
            return resp
        except ValueError as err:
            return {'error': 'Invalid password or email !'}, 401
        except Exception as err:
            return str(err), 500


@auth_api.route("/refresh_token")
class Refresh(Resource):
    @jwt_required(refresh=True, locations=['cookies'])
    def get(self):
        return AuthHandler.refresh()


@auth_api.route("/logout")
class Logout(Resource):
    @jwt_required(verify_type=False)
    def get(self):
        result = AuthHandler.logout()
        resp = make_response(result, 200)
        resp.delete_cookie('refresh_token')
        return resp
