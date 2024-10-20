from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE
from typing import Optional


from db import db


class BrandImages(db.Model):
    __tablename__ = 'brand_images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False, unique=True)
    image_url = db.Column(db.String, nullable=False)
    image_alt = db.Column(db.String, nullable=True)

    def __init__(self, brand_id: int, image_url: str, image_alt: Optional[str]=None):
        self.brand_id = brand_id
        self.image_url = image_url
        self.image_alt = image_alt if image_alt is not None else ''


class BrandImagesSchema(SQLAlchemyAutoSchema):
    class Meta:
        register = True
        model = BrandImages
        include_fk = True
        unknown = EXCLUDE

