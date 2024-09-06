from db import db
from src.models.user import User
from logging import getLogger


logger = getLogger(__name__)


class UserHandler:

    @classmethod
    def get_users(cls):
        return User.query.all()

    @classmethod
    def get_user_by_id(cls, user_id):
        return User.query.get(user_id)

    @classmethod
    def delete_user(cls, user_id):
        logger.info(user_id)
        user = User.query.filter_by(id=user_id).scalar()
        if user is not None:
            db.session.delete(user)
            db.session.commit()

        return user_id

    @classmethod
    def edit_user(cls, user_id, user):
        try:
            db.session.merge(user)
            db.session.commit()
        except Exception as e:
            return str(e)
        return User.query.get(user_id)

