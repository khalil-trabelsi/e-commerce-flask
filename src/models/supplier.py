from datetime import datetime

from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(220), unique=True, nullable=False)
    contact_name = db.Column(db.String(220), unique=True, nullable=False)
    email = db.Column(db.String(220), unique=True, nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(150))
    city = db.Column(db.String(150))
    zipcode = db.Column(db.String(35))
    country = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)

    def init(self, name, contact_name, email, phone, address, city, zipcode, country):
        self.name = name
        self.contact_name = contact_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.zipcode = zipcode
        self.country = country
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return "<Supplier %r>" % self.name


class SupplierSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Supplier
        register = True
        unknown = EXCLUDE

