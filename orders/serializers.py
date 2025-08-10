# serializers.py

from rest_framework import serializers

from Shop.models import Product
from Shop.serializers import ProductSerializer, StoreSerializer
from campusprofile.models import Student
from .models import Cart, Wishlist, Order, OrderItem, Payment


class ProductCartSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    store = StoreSerializer()

    class Meta:
        model = Product
        fields = ['id', 'image', 'price', 'product_name',
                  'category', 'variant', 'discount', 'store']

    def get_price(self, obj):
        return int(obj.price)

    # def get_store(self, obj):
    #     return StoreSerializer()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class CartSerializer(serializers.ModelSerializer):

    # price = serializers.CharField(
    #     source='product.price', read_only=True)
    # product = serializers.SerializerMethodField()
    product = ProductCartSerializer()
    # price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['user', 'added_at', 'product']

    # def get_product(self, obj):
    #     print()
    #     print("obj", obj)
    #     print()

    #     return ProductCartSerializer(obj.product, context=self.context).data

    # def get_image(self, obj):
    #     return obj.product.image


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Wishlist
        fields = ['user', 'added_on', 'product']
        read_only_fields = ['user', 'added_on']

    def get_serializer_context(self):
        return {"request": self.request}


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    # product = serializers.SerializerMethodField()
    # product = ProductCartSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.unit_price

    # def get_product(self, obj):
    #     print("Product obj", obj)
    #     product = Product.objects.filter(product_name=obj.product.product_name,
    #                                      category=obj.product.category).first()
    #     print("Product", product)
    #     # return ProductCartSerializer(obj.product).data

    #     return product


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    # store = StoreSerializer()

    class Meta:
        model = Order
        fields = ['id', 'student', 'store', 'ordered_at',
                  'delivery_date', 'status', 'items', 'payment_method', 'payment_status', 'payment_reference']
        read_only_fields = ['student', 'ordered_at']

    def validate(self, data):
        method = data.get('payment_method')
        status = data.get('payment_status')

        if method in ['card', 'bank'] and status != 'paid':
            raise serializers.ValidationError(
                "Online payments must be marked as paid.")
        if method == 'cash' and status != 'pending':
            raise serializers.ValidationError(
                "Cash orders must be marked as pending.")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        student = validated_data.pop('student')
        # product = validated_data.pop('product')
        print()
        print("validated_data", validated_data)
        print()
        print("items_data", items_data)
        print()
        # print("product", product)
        print()
        # student = Student.objects.filter(
        #     user=student).first()

        order = Order.objects.create(student=student, **validated_data)
        for item in items_data:
            print('ITems', item)
            # product_data = item.pop('product_data')
            # print('product_data', product_data)
            OrderItem.objects.create(order=order, **item)
        return order


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(
        source='student.user.username', read_only=True)
    # items = OrderItemSerializer(many=True)
    # store = StoreSerializer()

    class Meta:
        model = Student
        fields = ['username',]

    def get_username(self, obj):
        return obj.user.username


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    store = StoreSerializer()
    student = StudentSerializer()

    class Meta:
        model = Order
        fields = ['id', 'student', 'store', 'ordered_at',
                  'delivery_date', 'status', 'items', 'payment_method', 'payment_status', 'payment_reference']
        read_only_fields = ['student', 'ordered_at']

    def validate(self, data):
        method = data.get('payment_method')
        status = data.get('payment_status')

        if method in ['card', 'bank'] and status != 'paid':
            raise serializers.ValidationError(
                "Online payments must be marked as paid.")
        if method == 'cash' and status != 'pending':
            raise serializers.ValidationError(
                "Cash orders must be marked as pending.")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        student = validated_data.pop('student')
        # product = validated_data.pop('product')
        print()
        print("validated_data", validated_data)
        print()
        print("items_data", items_data)
        print()
        # print("product", product)
        print()
        # student = Student.objects.filter(
        #     user=student).first()

        order = Order.objects.create(student=student, **validated_data)
        for item in items_data:
            print('ITems', item)
            # product_data = item.pop('product_data')
            # print('product_data', product_data)
            OrderItem.objects.create(order=order, **item)
        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['paid_at']
