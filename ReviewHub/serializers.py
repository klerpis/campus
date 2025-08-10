from rest_framework import serializers

from Shop.models import Product
from .models import ProductReview
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class UserProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductContentSerializer()
    user = UserProductReviewSerializer()

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    product = ProductContentSerializer()
    user = UserProductReviewSerializer()

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class ProductCreateReviewSerializer(serializers.ModelSerializer):
    # product = ProductContentSerializer()
    # user = UserProductReviewSerializer()

    class Meta:
        model = ProductReview
        fields = ['product', 'rating', 'comment',]
        # read_only_fields = ['user', 'created_at']
