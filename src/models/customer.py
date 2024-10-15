from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE
from logging import getLogger

from db import db
from .user import User

logger = getLogger(__name__)

class Customer(User):
    __tablename__ = 'customers'
    id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    first_name = db.Column(db.String(80), unique=True, nullable=True)
    last_name = db.Column(db.String(80), unique=True, nullable=True)
    phone_number = db.Column(db.String(80), unique=True, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)

    def __init__(self, first_name, last_name, phone_number, birth_date, email, password, gender, role_id):
        logger.info(role_id)
        User.__init__(self, email, password, gender, role_id)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.birth_date = birth_date

    __mapper_args__ = {
        'polymorphic_identity': 2,
    }


class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_fk = True
        register = True
        unknown = EXCLUDE