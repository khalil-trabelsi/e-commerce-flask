from db import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)


class BrandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Brand
        register = True
        unknown = EXCLUDE
        include_fk = True
