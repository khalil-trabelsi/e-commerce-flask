from logging import getLogger
from flask import request, make_response, jsonify
from flask_restx import Resource, ValidationError, Namespace
from marshmallow import fields


from src.handlers.auth_handler import AuthHandler
from marshmallow_jsonschema import JSONSchema
from src.models.user import UserSchema
from src.web.schema import LoginArgsSchema
from flask_jwt_extended import jwt_required, current_user
from .schema import CustomerPostArgsSchema, UserGetSchema

logger = getLogger(__name__)

auth_api = Namespace('auth', description='Authentication related operations')


user_post_schema = UserSchema(exclude=['id', 'created_at', 'updated_at', 'token'])
user_post_model = auth_api.schema_model(
    'userPostSchema', JSONSchema().dump(user_post_schema)['definitions']['UserSchema']
)

user_get_schema = UserGetSchema(exclude=['updated_at', 'token', 'password'])
user_get_model = auth_api.schema_model(
    'userGetSchema', JSONSchema().dump(user_get_schema)['definitions']['UserGetSchema']
)

customer_register_schema = CustomerPostArgsSchema()
customer_register_model = auth_api.schema_model(
    'customerPostArgsSchema', JSONSchema().dump(customer_register_schema)['definitions']['CustomerPostArgsSchema']
)

login_args_schema = LoginArgsSchema()
login_args_model = auth_api.schema_model(
    'loginArgsSchema', JSONSchema().dump(login_args_schema)['definitions']['LoginArgsSchema']
)

@auth_api.route("/register", methods=['POST'])
class Register(Resource):
    @auth_api.expect(customer_register_model)
    @auth_api.response(201, 'User created Successfully', [customer_register_model])
    @auth_api.response(409, 'Validation Error: Bad Request')
    @auth_api.response(500, 'Internal Server Error')
    def post(self):
        try:
            data = customer_register_schema.load(request.json)
        except ValidationError as err:
            return str(err.msg), 400
        try:
            confirmation_token = AuthHandler.register(**data)
        except ValueError as err:
            return str(err), 409
        except Exception as err:
            logger.error(err)
            return {'error': str(err)}, 500
        return {'confirmation': confirmation_token}, 201


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


@auth_api.route("/confirm/<token>")
class Confirm(Resource):
    @jwt_required()
    def get(self, token):
        if current_user.is_confirmed:
            return jsonify({'message': 'You are already confirmed.'})
        try:
            is_confirmed = AuthHandler.confirm_email(token, current_user.email)
            if is_confirmed:
                return jsonify({'message': 'You have confirmed your account.'})
            else:
                return jsonify({'message': 'The confirmation link is invalid or has expired.'})
        except Exception as err:
            return jsonify({'error': str(err)})