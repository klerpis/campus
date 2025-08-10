from django.shortcuts import render

from rest_framework import generics, permissions, status

from campusprofile.models import Student
from .models import ProductReview
from .serializers import ProductReviewSerializer, ProductCreateReviewSerializer, ProductListSerializer
from rest_framework.exceptions import APIException, ValidationError


class VendorReviewListView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ProductReview.objects.filter(product__store__vendor__user=user)


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductCreateReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        # print()
        # print()
        # print("QUERY", dir(queryset))
        # print()
        # print()
        # print()
        if hasattr(user, 'vendor') and user.vendor.exists():
            return queryset.filter(product__store__vendor__user=user)
        return queryset

    def perform_create(self, serializer):
        print()
        print("serializer", serializer)
        print()
        student = Student.objects.filter(user=self.request.user).first()
        try:
            serializer.save(user=student)
        except Exception as e:
            print()
            print()
            print("BLDDY EERR", e)
            print()
            print()
            raise ValidationError(
                "Cant review more than once on a product", code=status.HTTP_401_UNAUTHORIZED)
            # return "Cant review more than once on a product"


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product__id=product_id)
