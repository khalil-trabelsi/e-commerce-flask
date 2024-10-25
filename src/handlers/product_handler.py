from flask import url_for
from sqlalchemy.exc import IntegrityError
from logging import getLogger

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from typing import Optional, List, Dict
import os

from db import db
from src.models.product import Product
from src.helpers.FileConf import allowed_file, get_upload_folder
from src.models.product_feature import ProductFeatures

from src.models.product_images import ProductImages

logger = getLogger(__name__)


class ProductHandler:

    @classmethod
    def get_all_products(cls):
        products = Product.query.all()
        for product in products:
            for image in product.images:
                image.image_url = url_for('static_uploaded_file', filename=image.image_url, _external=True)
        return products

    @classmethod
    def get_product_by_id(cls, product_id):
        products = Product.query.filter_by(id=product_id).first_or_404()
        for image in products.images:
            image.image_url = url_for('static_uploaded_file', filename=image.image_url, _external=True)
        return Product.query.filter_by(id=product_id).first_or_404()

    @classmethod
    def add_product(
            cls,
            name: str,
            price_ht: float,
            tva: float,
            brand_id: int,
            category_id: int,
            collection_id: int,
            features: List[Dict[str, str]],
    ):
        try:
            new_product = Product(name=name, price_ht=price_ht, tva=tva, brand_id=brand_id, category_id=category_id, collection_id=collection_id)
            db.session.add(new_product)
            db.session.commit()

            for feature in features:
                product_feature = ProductFeatures(label=feature['label'], product_id=new_product.id)
                db.session.add(product_feature)
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
    def add_product_images(cls, product_id: int, files: List[FileStorage], main_image: str):
        paths = []
        upload_folder = get_upload_folder()
        for f in files:
            logger.info(f)
            filename = secure_filename(f.filename)
            if filename != '' and allowed_file(filename):
                file_path = os.path.join(upload_folder, filename)
                f.save(file_path)
                paths.append(file_path)
                if filename == main_image:
                    product_image = ProductImages(product_id, filename, main_image=True)
                else:
                    product_image = ProductImages(product_id, filename)
                db.session.add(product_image)
                db.session.commit()

        return paths

