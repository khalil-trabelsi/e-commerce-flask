from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE


from db import db


class ShippingAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    postal = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    def __init__(self, street, city, country, postal, customer_id):
        self.street = street
        self.city = city
        self.country = country
        self.postal = postal
        self.customer_id = customer_id


class ShippingAddressSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ShippingAddress
        include_fk = True
        register = True
        unknown = EXCLUDE