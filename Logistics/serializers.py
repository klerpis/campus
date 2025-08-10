from rest_framework import serializers
from .models import Sale, Stock


class SaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.product_name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'product', 'store', 'product_name',
                  'total_price', 'refunded', 'quantity', 'sold_at']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'product', 'count']
