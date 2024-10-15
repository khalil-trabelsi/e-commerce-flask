from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE
from typing import Optional

from db import db


class ProductImages(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    image_url = db.Column(db.String(255))
    alt_text = db.Column(db.String(255), nullable=True)

    def __init__(self, product_id, image_url, alt_text: Optional[str] = None):
        self.product_id = product_id
        self.image_url = image_url
        self.alt_text = alt_text


class ProductImagesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductImages
        register = True
        include_fk = True
        unknown = EXCLUDE

