from logging import getLogger

from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from werkzeug.exceptions import RequestEntityTooLarge

from db import db
from flask_restx import Api
from flask_jwt_extended import JWTManager
from src.models.user import User, TokenBlockList
from flask_cors import CORS
from flask_mail import Mail

from src.web import brand_web

load_dotenv()

migrate = Migrate()
api = Api(version='1.0', title='Commerce API', description='API for e-commerce app')
jwtManager = JWTManager()
mail = Mail()

logger = getLogger()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        DATABASE_URL=os.getenv('DATABASE_URI'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
        JWT_COOKIE_HTTPONLY=True,
        JWT_TOKEN_LOCATION=['headers', 'cookies'],
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_PORT=os.getenv('MAIL_PORT'),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS'),
        MAIL_USE_SSL=os.getenv('MAIL_USE_SSL'),
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT'),
    )
    app.config.from_object(config_name)
    # app.config["MAIL_SERVER"] = "smtp.gmail.com",
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USERNAME'] = "trabelsiikhalil10@gmail.com"
    # app.config['MAIL_PASSWORD'] = "udus exvt cfte ytlp"
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USE_SSL'] = True

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwtManager.init_app(app)
    mail.init_app(app)

    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:4200","https://localhost:4200", "http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
     }})

    from src.models.stock_movement import StockMovement
    from src.models.product import Product

    # register apis
    from src.web.admin_web import admin_api
    from src.web.auth_web import auth_api
    from src.web.supplier_web import supplier_api
    from src.web.role_web import role_api
    from src.web.category_web import category_api
    from src.web.brand_web import brand_api
    from src.web.product_web import product_api
    from src.web.stock_movement_web import stock_movement_api
    from src.web.customer_web import customer_api
    from src.web.collection_web import collection_api
    from src.web.uploaded_file_web import uploaded_file_api

    api.add_namespace(admin_api)
    api.add_namespace(auth_api)
    api.add_namespace(supplier_api)
    api.add_namespace(role_api)
    api.add_namespace(category_api)
    api.add_namespace(brand_api)
    api.add_namespace(product_api)
    api.add_namespace(stock_movement_api)
    api.add_namespace(customer_api)
    api.add_namespace(collection_api)
    api.add_namespace(uploaded_file_api)

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

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error):
        return jsonify({"error": str(error)}), 413

    return app
