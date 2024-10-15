from flask import url_for
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from typing import Optional, List
import os
import re

from db import db
from src.models.product import Product
from src.helpers.FileConf import allowed_file, get_upload_folder


from src.models.product_images import ProductImages

logger = getLogger(__name__)


class ProductHandler:

    @classmethod
    def get_all_products(cls):
        logger.info(Product.query.all())
        return Product.query.all()

    @classmethod
    def get_product_by_id(cls, product_id):
        return Product.query.filter_by(id=product_id).first_or_404()

    @classmethod
    def add_product(
            cls,
            name: str,
            price_ht: float,
            tva: float,
            brand_id: int,
            category_id: int,
            description: Optional[str] = None,
    ):
        try:
            new_product = Product(name=name, price_ht=price_ht, tva=tva, brand_id=brand_id, category_id=category_id, description=description)
            db.session.add(new_product)
            db.session.commit()
            return new_product

        except IntegrityError as e:
            if 'uniqueViolation' in str(e.orig):
                raise ValueError(f"Product already exists, Detail: {str(e)}")
            else:
                raise Exception(str(e))
        except Exception as e:
            raise e

    @classmethod
    def add_product_images(cls, product_id: int, files: List[FileStorage]):
        paths = []
        upload_folder = get_upload_folder()
        for f in files:
            logger.info(f)
            filename = secure_filename(f.filename)
            if filename != '' and allowed_file(filename):
                file_path = os.path.join(upload_folder, filename)
                f.save(file_path)
                paths.append(file_path)
                product_image = ProductImages(product_id, url_for('products_serve_image', filename=filename, _external=True)
)
                db.session.add(product_image)
                db.session.commit()

        return paths

