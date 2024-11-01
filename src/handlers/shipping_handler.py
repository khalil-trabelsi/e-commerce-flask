from src.models.shipping_address import ShippingAddress
from db import db

from typing import Optional

class ShippingHandler():
    @classmethod
    def get_shipping_addresses(cls):
        return ShippingAddress.query.all()

    @classmethod
    def get_shipping_address_by_customer_id(cls, customer_id: int):
        return ShippingAddress.query.filter_by(customer_id=customer_id).scalar()

    @classmethod
    def add_shipping_address(cls, customer_id: int, street: str, city: str, country: str, postal: str):
        shipping_address = ShippingAddress(customer_id=customer_id, street=street, city=city, country=country, postal=postal)
        db.session.add(shipping_address)
        db.session.commit()

        return shipping_address

    @classmethod
    def edit_shipping_address(cls, customer_id: int, street: Optional[str] = None, city: Optional[str] = None,
                              country: Optional[str] = None, postal: Optional[str] = None):
        existing_shipping_address = cls.get_shipping_address_by_customer_id(customer_id)

        new_fields_data = {
            'street': street,
            'city': city,
            'country': country,
            'postal': postal
        }

        new_fields_data = {key: value for key, value in new_fields_data.items() if value is not None}
        for (key, value) in new_fields_data.items():
            setattr(existing_shipping_address, key, value)

        db.session.merge(existing_shipping_address)
        db.session.commit()
