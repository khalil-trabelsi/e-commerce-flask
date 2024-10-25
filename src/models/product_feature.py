from marshmallow import EXCLUDE

from db import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class ProductFeatures(db.Model):
    table_name = 'product_features'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    def __init__(self, label, product_id):
        self.label = label
        self.product_id = product_id


class ProductFeaturesSchema(SQLAlchemyAutoSchema):
    class Meta:
        register = True
        model = ProductFeatures
        unknown = EXCLUDE