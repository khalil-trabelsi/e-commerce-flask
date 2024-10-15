from datetime import datetime, timezone

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE
from db import db


class DeliveryLine(db.Model):
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    stock_movement_id = db.Column(db.Integer, db.ForeignKey('stock_movements.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.TIMESTAMP, nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('product_id', 'stock_movement_id'),
    )

    def __init__(self, product_id, stock_movement_id, quantity):
        self.product_id = product_id
        self.stock_movement_id = stock_movement_id
        self.quantity = quantity
        self.date = datetime.now(timezone.utc)


class DeliveryLineSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeliveryLine
        register = True
        include_fk = True
        unknown = EXCLUDE

