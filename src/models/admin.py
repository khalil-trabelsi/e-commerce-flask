from db import db
from .user import User


class Admin(User):
    __tablename__ = 'admin'
    id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)

    def __init__(self, username, password, email, role_id, gender, is_confirmed, confirmed_on):
        User.__init__(self, email, password, gender, role_id, is_confirmed, confirmed_on)
        self.username = username

    __mapper_args__ = {
        'polymorphic_identity': 1,
    }