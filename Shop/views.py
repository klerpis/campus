from Logistics.models import Stock
from .filters import ProductFilter  # we'll define this next
from campusprofile.models import Vendor
from .serializers import StoreSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsVendor
from .serializers import ProductSerializer
from rest_framework import (
    generics, filters, serializers,
    viewsets, permissions, status,
)
from django.shortcuts import render
from rest_framework.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .models import Product, Category, Store, StoreType
from .serializers import (ProductSerializer, CategorySerializer, StoreTypeSerializer,
                          StoreSerializer, StorePreviewSerializer, StoreCreateSerializer)
import django_filters


# class ProductListView(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


# class ProductDetailView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     lookup_field = 'id'


class StoreViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  #

    # POST /shop/store/to_create/
    @action(detail=False, methods=['post'], permission_classes=[IsVendor])
    def to_create(self, request):
        if Store.objects.filter(vendor__user=request.user).exists():
            return Response({"detail": "Store already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StoreCreateSerializer(data=request.data)
        print()
        print("UNLMITED data", request.data)
        print()
        print("UNLMITED data", serializer)
        print()
        if serializer.is_valid():
            print("to create a store is a pain in the ass",
                  serializer, request.user.vendor, )
            vendor = Vendor.objects.filter(user=request.user).first()
            print("1")
            store = serializer.save()
            print("2")
            vendor.store = store
            print("3")
            vendor.save()
            print("4")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("serializer.errors", serializer.errors)
        print()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET /shop/store/me/
    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            # if not request.user.is_authenticated:
            #     raise Store.DoesNotExist
            # print('ME one', request.user, request.user.vendor,
            #       request.user.vendor.exists())
            # vendor = Vendor.objects.filter(user=request.user).first()
            print('ME one', request, request.user)
            store = Store.objects.get(vendor__user=request.user)
            print('ME two', request, store)
            serializer = StoreSerializer(store, context={'request': request})
            # print('ME three')
            return Response(serializer.data)
        except Store.DoesNotExist as e:
            print()
            print("miserable error", e)
            print()
            raise NotFound("Store not created yet.")

    # PATCH /shop/store/to_update/
    @action(detail=False, methods=['patch'], permission_classes=[IsVendor])
    def to_update(self, request):
        try:
            # store = Store.objects.get(vendor=request.user)
            vendor = Vendor.objects.filter(user=request.user).first()
            store = Store.objects.get(vendor=vendor)

            if not store.approved:
                return Response({"detail": "Cannot edit store before approval."}, status=status.HTTP_403_FORBIDDEN)

            serializer = StoreSerializer(
                store, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Store.DoesNotExist:
            raise NotFound("Store not found.")


class StoreTypesListView(generics.ListAPIView):
    queryset = StoreType.objects.all()
    serializer_class = StoreTypeSerializer


class ApprovedStoreListView(generics.ListAPIView):
    serializer_class = StorePreviewSerializer
    queryset = Store.objects.filter(approved=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['category']
    search_fields = ['store_name', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        print()
        print("queryset", [(i.logo,) for i in queryset])
        print()
        return queryset


class StoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.filter(approved=True)
    serializer_class = StoreSerializer
    lookup_field = 'id'


# class ProductFilter(django_filters.FilterSet):
#     min_price = django_filters.NumberFilter(
#         field_name="price", lookup_expr='gte')
#     max_price = django_filters.NumberFilter(
#         field_name="price", lookup_expr='lte')

#     class Meta:
#         model = Product
#         fields = ['category', 'store']


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# class StoreListView(generics.ListAPIView):
#     queryset = Store.objects.all()
#     serializer_class = StoreSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter

    search_fields = [
        'product_name',
        'store__store_name',
        'store__vendor__first_name'
    ]

    ordering_fields = ['price', 'discount']

    # def perform_create(self, serializer):
    #     try:
    #         print("origin traced listed product problem")
    #         store = Store.objects.get(vendor=self.request.user)
    #     except Store.DoesNotExist:
    #         raise serializers.ValidationError("Vendor store not found.")

    #     serializer.save(store=store)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        print()
        print()
        print("QUERY", dir(queryset))
        print()
        print()
        print()
        if hasattr(user, 'vendor') and user.vendor.exists():
            return queryset.filter(store__vendor__user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            store = Store.objects.get(vendor__user=request.user)
        except Store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_400_BAD_REQUEST)

        # stock_count = request.data.pop('stock', None)
        data = request.data.copy()
        stock_count = data.pop('stock', None)
        if not stock_count:
            raise ValidationError("Please Indicate the Stock count")

            # Serialize product (excluding stock)
        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the product, attach store manually
        product = serializer.save(store=store)

        # Create stock only if count is provided
        # if stock_count is not None:
        if isinstance(stock_count, list):
            stock_count = stock_count[0]
            # print("found the guilty dude")
        try:
            print("stock count", stock_count, request.data)
            Stock.objects.create(product=product, count=int(stock_count))
        except Exception as e:
            # Rollback product if stock fails
            product.delete()
            return Response({"detail": f"Stock creation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        return {"request": self.request}
    # def perform_create(self, serializer):
    #     # vendor = self.request.user.vendor
    #     serializer.save()  # If you later attach vendor/store, you can modify this


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        return {"request": self.request}
