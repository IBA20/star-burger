from rest_framework.serializers import ModelSerializer

from .models import Order, OrderPosition


class OrderPositionSerializer(ModelSerializer):
    class Meta:
        model = OrderPosition
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderPositionSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address']
