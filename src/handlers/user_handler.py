from db import db
from src.models.admin import Admin
from src.models.user import User
from src.models.customer import Customer
from logging import getLogger
from typing import Optional
from sqlalchemy.orm import with_polymorphic, selectinload

logger = getLogger(__name__)


class UserHandler:

    @classmethod
    def get_users(cls):
        return User.query.filter(User.role_id != 2).all()

    @classmethod
    def get_user_by_id(cls, user_id):
        return User.query.filter_by(id=user_id).first_or_404()

    @classmethod
    def delete_user(cls, user_id):
        logger.info(user_id)
        user = User.query.filter_by(id=user_id).scalar()
        if user is not None:
            db.session.delete(user)
            db.session.commit()

        return user_id

    @classmethod
    def edit_user(
            cls,
            user_id: int,
            email: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[int] = None,
            phone_number: Optional[str] = None,
            gender: Optional[str] = None,
            status: Optional[str] = None
    ):
        new_fields_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "gender": gender,
            "status": status
        }
        user = cls.get_user_by_id(user_id)
        new_fields_data = {key: value for (key, value) in new_fields_data.items() if value is not None}
        for key, value in new_fields_data.items():
            setattr(user, key, value)
        try:
            db.session.merge(user)
            db.session.commit()
        except Exception as e:
            return str(e)
        return user

    @classmethod
    def get_customers(cls):
        customer_polymorphic = with_polymorphic(User, [Customer])
        logger.info(db.session.query(customer_polymorphic).filter(customer_polymorphic.role_id == 2))
        return db.session.query(customer_polymorphic).filter(customer_polymorphic.role_id == 2).all()

    @classmethod
    def get_admins(cls):
        admin_polymorphic = with_polymorphic(User, [Admin])
        return db.session.query(admin_polymorphic).filter(admin_polymorphic.role_id == 1).all()
