import decimal

from Logistics.models import Stock
from orders.models import Wishlist
from .models import Product
from rest_framework import serializers
from .models import Product, Category, Store, StoreType


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name']


class StoreTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreType
        fields = ['id', 'name']


class StoreCreateSerializer(serializers.ModelSerializer):
    # store_type = StoreTypeSerializer()
    # logo = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ['store_name', 'address', 'logo',
                  'description', 'store_type',]


class StoreSerializer(serializers.ModelSerializer):
    store_type = StoreTypeSerializer()
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ['id', 'store_name', 'address', 'logo',
                  'description', 'approved', 'store_type', 'created_at']

    def get_logo(self, obj):
        request = self.context.get('request')
        print("request for LOGO", obj.logo)
        if obj.logo and hasattr(obj.logo, 'url'):
            result = request.build_absolute_uri(
                obj.logo.url) if request else obj.logo.url
            print("LOGO", result, self.context)
            return result
        return None

# shop/serializers.py


class TopProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'image', 'price']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class StorePreviewSerializer(serializers.ModelSerializer):
    top_products = serializers.SerializerMethodField()
    store_type = StoreTypeSerializer()

    class Meta:
        model = Store
        fields = ['id', 'store_name', 'description', 'logo',
                  'description', 'approved', 'store_type', 'created_at',
                  'top_products']

    def get_top_products(self, store):
        products = Product.objects.filter(store=store)[:3]
        return TopProductSerializer(products, many=True, context=self.context).data


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    variant = serializers.StringRelatedField()  # or ProductSerializer if recursive
    store = StoreSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'price', 'category', 'variant',
            'discount', 'store'
        ]


class ProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    stock_count = serializers.CharField(
        source='stock.count', read_only=True)
    store_name = serializers.CharField(
        source='store.store_name', read_only=True)
    # store_logo = serializers.ImageField(source='store.logo', read_only=True)

    # is_wishlisted = serializers.SerializerMethodField()
    # product_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'price', 'image',
            'category', 'variant', 'store_name',
            'discount', 'store', 'final_price',
            'description', 'stock_count',
        ]
        read_only_fields = ['store']

    # def get_stock_count(self, obj):
    #     return getattr(obj.stock, 'count', None)

    # def get_is_wishlisted(self, obj):
    #     user = self.context.get('request').user
    #     if user.is_authenticated:
    #         return Wishlist.objects.filter(user=user, product=obj).exists()
    #     return False
    # def get_product_quantity(self, obj):
    #     Stock.objects.filter().first()

    def get_final_price(self, obj):
        return round(decimal.Decimal(obj.price) * decimal.Decimal((1 - ((obj.discount or 0) / 100))), 2)


# class ProductSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'product_name', 'price', 'image', 'category', 'variant',
#             'discount', 'store',
#         ]
