from datetime import datetime, timezone
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE, fields
from db import db
from .product_feature import ProductFeaturesSchema
from .product_images import ProductImages, ProductImagesSchema
from .brand import Brand, BrandSchema
from .category import Category, CategorySchema
from .collection import Collection, CollectionSchema


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    price_ht = db.Column(db.Float, nullable=False)
    tva = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    available = db.Column(db.Boolean, nullable=False, default=False)
    stock = db.Column(db.Integer, nullable=False)
    images = db.relationship('ProductImages', backref='product', lazy='joined')
    brand = db.relationship('Brand', backref='product', lazy='joined')
    category = db.relationship('Category', backref='product', lazy='joined')
    collection = db.relationship('Collection', backref='product', lazy='joined')
    features = db.relationship('ProductFeatures', backref='product', lazy='joined')

    def __init__(self, name, price_ht, tva, brand_id, category_id, collection_id):
        self.name = name
        self.price_ht = price_ht
        self.tva = tva
        self.brand_id = brand_id
        self.category_id = category_id
        self.created_at = datetime.now(timezone.utc)
        self.stock = 0
        self.available = False
        self.price = price_ht + (price_ht * (tva / 100))
        self.collection_id = self.collection_id

    def __repr__(self):
        return 'Product %r' % self.images


class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        register = True
        unknown = EXCLUDE
        include_fk = True

    images = fields.Nested(ProductImagesSchema, many=True, only=['image_url', 'alt_text', 'main_image'])
    alt_text = fields.String(allow_none=True)
    brand = fields.Nested(BrandSchema, only=['name'])
    category = fields.Nested(CategorySchema, only=['name'])
    collection = fields.Nested(CollectionSchema, only=['name'])
    features = fields.Nested(ProductFeaturesSchema, only=['label'], many=True)
