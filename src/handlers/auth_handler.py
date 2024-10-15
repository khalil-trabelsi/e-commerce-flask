
from logging import getLogger
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic
from datetime import date, timedelta, datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from src.models.user import UserSchema, TokenBlockList
from flask import request, url_for
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import os


from src.models.admin import Admin
from src.models.customer import Customer
from src.models.user import User
from db import db
from src.helpers.email import send_email


logger = getLogger(__name__)
load_dotenv()


class AuthHandler:
    @classmethod
    def login(cls, email: str, password: str) -> any:
        user = cls.get_user_by_email(email)
        if user is not None and cls._check_password(user.password, password):
            user.token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(hours=48),
            )
            db.session.commit()
            token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=0.5),
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
            return {"error": "Token is invalid or revoked"}, 401
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
    def register(
            cls,
            email: str,
            password: str,
            birth_date: Optional[date] = None,
            username: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            phone_number: Optional[str] = None,
            gender: Optional[str] = None,
            role_id: Optional[int]=None
    ) -> User | str:
        try:
            hashed_password = cls._set_password(password)
            if first_name is not None and last_name is not None:
                user = Customer(first_name, last_name, phone_number, birth_date, email, hashed_password, gender, role_id)
            else:
                user = Admin(username=username, password=hashed_password, email=email, role_id=role_id, gender=gender,
                             is_confirmed=True, confirmed_on=datetime.now(timezone.utc))

            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if 'user_email_key' in str(e.orig):
                raise ValueError("L'adresse mail est déjà utilisée")
            raise ValueError(f"Une erreur s'est produite {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValueError(str(e))
        token = cls.generate_token(user.email)
        confirm_url = url_for('auth_confirm', token=token, _external=True)
        subject = 'Account activation link'
        html = f"""
            <p> 
              Welcome! Thanks for signing up. Please follow this link to activate your account: 
            </p> 
            <p><a href="https://localhost:4200/confirmation/{token}">https://localhost:4200/confirmation/{token}</a></p> 
            <br />
        """
        send_email(user.email, subject, html)
        return token

    @classmethod
    def _set_password(cls, password):
        return generate_password_hash(password, method='pbkdf2:sha256')

    @classmethod
    def _check_password(cls, hashed_password, password) -> bool:
        return check_password_hash(hashed_password, password)

    @classmethod
    def get_user_by_email(cls, email):
        customer_polymorphic = with_polymorphic(User, [Admin, Customer])
        logger.info(db.session.query(customer_polymorphic).filter_by(email=email).all())
        return db.session.query(customer_polymorphic).filter_by(email=email).scalar()
        # return User.query.filter_by(email=email).scalar()

    @classmethod
    def generate_token(cls, email):
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        return serializer.dumps(email, salt=os.getenv('SECURITY_PASSWORD_SALT'))

    @classmethod
    def confirm_token(cls, token, expiration=3600):
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        try:
            email = serializer.loads(token, salt=os.getenv('SECURITY_PASSWORD_SALT'),  max_age=expiration)
            return email
        except Exception:
            return False

    @classmethod
    def confirm_email(cls, token, user_email):
        email = cls.confirm_token(token)
        user = User.query.filter_by(email=user_email).first_or_404()

        if user.email == email:
            user.is_confirmed = True
            user.confirmed_on = datetime.now(timezone.utc)
            db.session.add(user)
            db.session.commit()
            return True

        return False
