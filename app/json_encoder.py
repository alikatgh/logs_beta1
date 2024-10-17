from flask.json import jsonify
from json import JSONEncoder as BaseJSONEncoder
from .models import Delivery, DeliveryItem, Supermarket, Subchain, Product


class CustomJSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Delivery):
            return {
                'id': obj.id,
                'delivery_date': obj.delivery_date.isoformat(),
                'supermarket': {
                    'id': obj.supermarket.id,
                    'name': obj.supermarket.name
                },
                'subchain': {
                    'id': obj.subchain.id,
                    'name': obj.subchain.name
                } if obj.subchain else None,
                'items': [
                    {
                        'id': item.id,
                        'product': {
                            'id': item.product.id,
                            'name': item.product.name
                        },
                        'quantity': item.quantity,
                        'price': item.price
                    }
                    for item in obj.items
                ]
            }
        return super().default(obj)
