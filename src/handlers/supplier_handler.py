from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import NoResultFound

from db import db
from src.models.supplier import Supplier


class SupplierHandler:

    @classmethod
    def get_suppliers(cls):
        return Supplier.query.all()

    @classmethod
    def get_supplier_by_id(cls, supplier_id):
        return Supplier.query.filter_by(id=supplier_id).scalar()

    @classmethod
    def add_supplier(cls, name, contact_name, email, phone, address, city, zipcode, country):
        supplier = Supplier(name=name, contact_name=contact_name, email=email, phone=phone, address=address, city=city, zipcode=zipcode, country=country)
        supplier.created_at = datetime.now(timezone.utc)
        supplier.updated_at = datetime.now(timezone.utc)
        try:
            db.session.add(supplier)
            db.session.commit()
            return supplier
        except Exception as e:
            db.session.rollback()
            return str(e)

    @classmethod
    def delete_supplier(cls, supplier_id: int):
        supplier = cls.get_supplier_by_id(supplier_id)
        db.session.delete(supplier)
        db.session.commit()

    @classmethod
    def update_supplier(
            cls,
            supplier_id: int,
            name: Optional[str] = None,
            contact_name: Optional[str] = None,
            email: Optional[str] = None,
            phone: Optional[str] = None,
            address: Optional[str] = None,
            city: Optional[str] = None,
            zipcode: Optional[str] = None,
            country: Optional[str] = None
                        ):
        supplier = cls.get_supplier_by_id(supplier_id)

        if supplier is None:
            raise NoResultFound("Supplier not found")

        new_fields_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "zipcode": zipcode,
            "country": country,
            "updates_at": datetime.now(timezone.utc)
        }

        new_fields_data = {key: value for (key, value) in new_fields_data.items() if value is not None}

        for key, value in new_fields_data.items():
            setattr(supplier, key, value)
        db.session.merge(supplier)
        db.session.commit()

        return supplier
