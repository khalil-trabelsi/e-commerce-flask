from db import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE, fields
from .brand_images import BrandImagesSchema


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.relationship('BrandImages', backref='brand', lazy='joined', uselist=False)


class BrandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Brand
        register = True
        unknown = EXCLUDE
        include_fk = True

    image = fields.Nested(BrandImagesSchema, only=('image_url', 'image_alt'))