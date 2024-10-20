import os

from flask import url_for
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from db import db
from src.models.brand import Brand
from src.models.brand_images import BrandImages
from typing import Optional
from logging import getLogger

from src.helpers.FileConf import get_upload_folder, allowed_file

logger = getLogger(__name__)


class BrandHandler:
    @classmethod
    def get_all_brands(cls):
        brands = Brand.query.all()
        for brand in brands:
            brand.image.image_url = url_for('static_uploaded_file', filename=brand.image.image_url, _external=True)
        return brands

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
        db.session.delete(brand_id)
        db.session.commit()

    @classmethod
    def add_brand_image(cls, brand_id: int, file: FileStorage, image_alt: Optional[str] = None):
        upload_folder = get_upload_folder()
        filename = secure_filename(file.filename)
        if filename != '' and allowed_file(filename):
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            brand_image = BrandImages(brand_id=brand_id, image_url=filename, image_alt=image_alt)
            db.session.add(brand_image)
            db.session.commit()

            return file_path



