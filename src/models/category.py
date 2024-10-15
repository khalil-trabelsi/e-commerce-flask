from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import CheckConstraint

from db import db


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent = db.relationship('Category', remote_side=[id], backref='children', lazy='joined')
    __table_args__ = (
      CheckConstraint('id != parent_id', name='check_id_not_equal_parent_id'),
    )


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        unknown = EXCLUDE
        register = True
        include_fk = True

    parent = fields.Nested('CategorySchema', exclude=('parent',), allow_none=True)
    children = fields.Nested('CategorySchema', many=True, exclude=('parent',), allow_none=True)
