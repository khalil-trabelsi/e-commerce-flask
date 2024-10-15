from src.models.delivery_line import DeliveryLine


class DeliveryLineHandler:

    @classmethod
    def get_delivery_line(cls, product_id: int, stock_movement_id: int):
        return DeliveryLine.query.filter_by(product_id=product_id, stock_movement_id=stock_movement_id).first()
