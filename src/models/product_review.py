from datetime import datetime, timezone

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from db import db
from typing import Optional
from marshmallow import EXCLUDE


class ProductReview(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))

    def __init__(self,
                 product_id: int,
                 title: str,
                 comment: str,
                 rating: int,
                 user_id: Optional[int] = None,
                 username: Optional[str] = None) -> None:
        self.product_id = product_id
        self.user_id = user_id
        self.username = username
        self.title = title
        self.comment = comment
        self.rating = rating


class ProductReviewSchema(SQLAlchemyAutoSchema):
    class Meta:
        register = True
        model = ProductReview
        include_fk = True
        unknown = EXCLUDE
