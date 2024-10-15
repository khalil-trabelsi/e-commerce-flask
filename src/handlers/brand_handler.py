from db import db
from src.models import brand
from src.models.brand import Brand
from typing import Optional


class BrandHandler:
    @classmethod
    def get_all_brands(cls):
        return Brand.query.all()

    @classmethod
    def add_brand(cls, name: str, description: Optional[str] = None):
        brand = Brand(name=name, description=description)
        db.session.add(brand)
        db.session.commit()
        return brand

    @classmethod
    def get_brand_by_id(cls, user_id: int):
        return Brand.query.filter_by(id=user_id).first_or_404()

    @classmethod
    def update_brand(cls, brand_id: int, name: Optional[str] = None, description: Optional[str] = None):
        brand = cls.get_brand_by_id(brand_id)
        if name is not None:
            brand.name = name
        if description is not None:
            brand.description = description

        db.session.merge(brand)
        db.session.commit()
        return brand

    @classmethod
    def delete_brand(cls, brand_id: int):
        db.session.delete(brand)
        db.session.commit()