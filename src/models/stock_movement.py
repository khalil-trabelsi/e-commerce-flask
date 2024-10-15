from datetime import datetime, timezone
from typing import Optional

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE, fields
from .product import Product, ProductSchema
from .supplier import Supplier, SupplierSchema
from .user import User, UserSchema
from db import db


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    reference = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movement_type = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now(timezone.utc))
    product = db.relationship(Product, backref='stock_movement', uselist=False, lazy='joined')
    supplier = db.relationship(Supplier, backref='stock_movement', uselist=False, lazy='joined')
    modified_by = db.relationship(User, backref='stock_movement', lazy='joined')
    comment = db.Column(db.String, nullable=True)

    def __init__(self, product_id, supplier_id, reference, user_id, movement_type, quantity, comment: Optional[str] = None):
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.reference = reference
        self.user_id = user_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.comment = comment


class StockMovementSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = StockMovement
        register = True
        include_fk = True
        unknown = EXCLUDE

    product = fields.Nested(ProductSchema, only=['name'])
    supplier = fields.Nested(SupplierSchema, only=['name'])
    modified_by = fields.Nested(UserSchema)

