from logging import getLogger

from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from db import db
from flask_restx import Api
from flask_jwt_extended import JWTManager, get_jwt_identity
from src.models.user import User, TokenBlockList
from flask_cors import CORS

load_dotenv()

migrate = Migrate()
api = Api()
jwtManager = JWTManager()

logger = getLogger()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        DATABASE_URL=os.getenv('DATABASE_URI'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        JWT_COOKIE_HTTPONLY=True,
        JWT_TOKEN_LOCATION=['headers', 'cookies'],
    )
    app.config.from_object(config_name)

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwtManager.init_app(app)

    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:4200","https://localhost:4200", "http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
     }})
    # register apis
    from src.web.user_web import user_api
    from src.web.auth_web import auth_api
    api.add_namespace(user_api)
    api.add_namespace(auth_api)

    # identify authenticated user
    @jwtManager.user_identity_loader
    def user_identity_lookup(user_id: int):
        return user_id
    # load user
    @jwtManager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        return User.query.filter_by(id=identity).one_or_none()

    # jwt error handlers
    @jwtManager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"error": 'Token has expired'}), 401

    @jwtManager.invalid_token_loader
    def expired_token_callback(error):
        return jsonify({"error": 'Invalid token'}), 401

    @jwtManager.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"error": str(error)}), 401

    @jwtManager.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_data) -> bool:
        jti = jwt_data["jti"]
        token = db.session.query(TokenBlockList).filter_by(jti=jti).scalar()
        return token is not None

    return app
