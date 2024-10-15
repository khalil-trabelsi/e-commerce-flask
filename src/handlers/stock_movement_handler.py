from typing import List, Optional
from sqlalchemy import and_
from logging import getLogger

from db import db
from src.handlers.product_handler import ProductHandler
from src.models.stock_movement import StockMovement


product_handler = ProductHandler()

logger = getLogger(__name__)

class StockMovementHandler:
    @classmethod
    def get_stock_movements(
            cls,
            suppliers_id: Optional[List[int]] = None,
            products_id: Optional[List[int]] = None,
            min_quantity: Optional[int] = None,
            max_quantity: Optional[int] = None
    ):

        filters = []
        logger.info(min_quantity)
        if len(suppliers_id):
            filters.append(StockMovement.supplier_id.in_(suppliers_id))
        if len(products_id):
            filters.append(StockMovement.product_id.in_(products_id))
        if min_quantity:
            filters.append(StockMovement.quantity >= min_quantity)
        if max_quantity:
            filters.append(StockMovement.quantity <= max_quantity)
        if len(filters) > 0:
            return StockMovement.query.filter(and_(*filters))

        return StockMovement.query.all()

    @classmethod
    def add_stock_movement(cls, product_id, supplier_id, reference, movement_type, user_id, quantity):
        stock_movement = StockMovement(product_id, supplier_id, reference, user_id, movement_type, quantity)
        db.session.add(stock_movement)
        db.session.commit()

        product = product_handler.get_product_by_id(product_id)
        product.stock += quantity
        product.available = True

        db.session.merge(product)
        db.session.commit()

        return stock_movement




