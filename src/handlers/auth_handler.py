
from logging import getLogger

from sqlalchemy.exc import IntegrityError

from src.models.user import User
from db import db
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from src.models.user import UserSchema, TokenBlockList
from flask import request

logger = getLogger(__name__)

user_schema = UserSchema(only=("id", "email", "birth_date", "first_name", "last_name", "phone_number", 'gender'))


class AuthHandler:
    @classmethod
    def login(cls, email: str, password: str) -> any:
        user = cls.get_user_by_email(email)
        logger.info(user)
        if user is not None and cls._check_password(user.password, password):
            user.token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(hours=48),
            )
            db.session.commit()
            token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(minutes=0.5),
            )
            return {'user': user, 'token': token, 'refresh_token': user.token}
        else:
            raise ValueError(Exception(''))

    @classmethod
    def refresh(cls):
        identity = get_jwt_identity()
        user = User.query.get(identity)
        current_refresh_token = request.cookies['refresh_token_cookie']
        if user.token != current_refresh_token:
            return {"msg": "Token is invalid or revoked"}, 401
        new_access_token = create_access_token(
                identity=identity,
                expires_delta=timedelta(hours=0.5))
        return {'token': new_access_token}

    @classmethod
    def logout(cls):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        jti = get_jwt()["jti"]
        token_type = get_jwt()['type']
        db.session.add(TokenBlockList(jti=jti))
        db.session.commit()
        user.revoke_refresh_token()
        return {'message': f'user logged out {token_type}'}

    @classmethod
    def register(cls, first_name: str, last_name: str, email: str, password: str, birth_date: date, phone_number: str, gender: str, role: int=None) -> User | str:
        try:
            hashed_password = cls._set_password(password)
            if role is not None:
                user = User(email, hashed_password, birth_date, first_name, last_name, phone_number, gender, role)
            else :
                user = User(email, hashed_password, birth_date, first_name, last_name, phone_number, gender)
            logger.info(user)
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if 'user_email_key' in str(e.orig):
                raise ValueError("L'adresse e-mail est déjà utilisée")
            raise ValueError("Une erreur inconnu s'est produite")
        except Exception as e:
            db.session.rollback()
            raise ValueError(str(e))
        return user

    @classmethod
    def _set_password(cls, password):
        return generate_password_hash(password, method='pbkdf2:sha256')

    @classmethod
    def _check_password(cls, hashed_password, password) -> bool:
        return check_password_hash(hashed_password, password)

    @classmethod
    def get_user_by_email(cls, email):
        return User.query.filter_by(email=email).scalar()