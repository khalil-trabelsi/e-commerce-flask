from sqlalchemy.exc import IntegrityError

from src.models.category import Category
from typing import Optional
from db import db


class CategoryHandler():
    @classmethod
    def get_all_categories(cls):
        return Category.query.all()

    @classmethod
    def get_category_by_id(cls, category_id):
        category = Category.query.filter_by(id=category_id).first_or_404()
        return category

    @classmethod
    def get_category_by_name(cls, category_name):
        category = Category.query.filter_by(name=category_name).first_or_404()

        return category

    @classmethod
    def add_category(cls, name, description: Optional[str] = None, parent_id: Optional[int] = None):
        fields_data = {
            'name': name,
            'description': description,
            'parent_id': parent_id
        }

        fields_data = {key: value for key, value in fields_data.items() if value is not None}
        category = Category(**fields_data)
        try:
            db.session.add(category)
            db.session.commit()
            return category
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError('Category name already exists')
        except Exception as e:
            db.session.rollback()
            raise Exception(str(e))

    @classmethod
    def delete_category(cls, category_id):
        category = cls.get_category_by_id(category_id)
        db.session.delete(category)
        db.session.commit()

    @classmethod
    def update_category(cls, category_id, name: Optional[str] = None, description: Optional[str] = None, parent_id: Optional[int] = None):
        category = cls.get_category_by_id(category_id)

        fields_data = {
            'name': name,
            'description': description,
            'parent_id': parent_id
        }

        fields_data = {key: value for key,value in fields_data.items() if value is not None}
        for key, value in fields_data.items():
            setattr(category, key, value)
        db.session.merge(category)
        db.session.commit()


