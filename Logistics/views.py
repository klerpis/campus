from rest_framework.pagination import PageNumberPagination
from Shop.models import Product, Store
from .models import Sale
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status, permissions
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from Logistics.models import Sale, SaleLog
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.shortcuts import render

# Create your views here.

from rest_framework import (generics, permissions,
                            status, filters, serializers)
from rest_framework.response import Response
from .models import Sale, Stock, SaleLog
from .serializers import SaleSerializer, StockSerializer
from Shop.models import Product
from Shop.permissions import IsVendor  # optional
from django_filters.rest_framework import DjangoFilterBackend

# Stock View (List & Update)


class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockUpdateView(generics.UpdateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    lookup_field = 'id'


# Sale View
class SaleListCreateView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'store', 'refunded']
    ordering_fields = ['sold_at', 'total_price']

    def get_queryset(self):
        sale = Sale.objects.filter(store__vendor__user=self.request.user)
        return sale
        # super().get_queryset()

    def perform_create(self, serializer):
        sale = serializer.save()
        try:
            stock = Stock.objects.get(product=sale.product)
            if stock.count < sale.quantity:
                raise serializers.ValidationError(
                    "Not enough stock available.")
            stock.count -= sale.quantity
            stock.save()
        except Stock.DoesNotExist:
            raise serializers.ValidationError(
                "No stock entry found for this product.")


class RefundSaleView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sale.objects.all()

    def patch(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)

        # Optional: Only allow vendor of the store or superuser
        if request.user != sale.store.vendor.user and not request.user.is_superuser:
            raise PermissionDenied("You're not allowed to refund this sale.")

        if sale.refunded:
            return Response({"detail": "Sale already refunded."}, status=status.HTTP_400_BAD_REQUEST)

        sale.refunded = True
        sale.save()

        SaleLog.objects.create(
            sale=sale,
            action='refunded',
            performed_by=request.user
        )

        return Response({"detail": "Sale refunded successfully."}, status=status.HTTP_200_OK)


# sales/views.py
class VendorSaleListView(generics.ListAPIView):
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        vendor = getattr(self.request.user, 'vendor', None)
        if not vendor or not hasattr(vendor, 'store'):
            return Sale.objects.none()

        queryset = Sale.objects.filter(
            store=vendor.store).select_related('product')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start and end:
            queryset = queryset.filter(sold_at__range=[start, end])

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(product__product_name__icontains=search)

        return queryset.order_by('-sold_at')


class VendorAnalyticsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print()
        print()
        print("USER", user)
        vendor = getattr(user, 'vendor', None)
        print("VENDOR", vendor, type(vendor))
        print("VENDOR", vendor.first().store)
        print("VENDOR exists", vendor.exists(), hasattr(vendor, 'store'))
        print(dir(vendor))
        print()
        # vendor = vendor or
        if not vendor and \
            not hasattr(vendor, 'first') and \
                not hasattr(vendor.first(), 'store'):

            return Response({"error": "No store found for vendor."}, status=400)

        store = vendor.first().store
        # store = Store.objects.all().first()  # the cheater will be removed

        sales = Sale.objects.filter(store=store, refunded=False)
        recent_sales = Sale.objects.filter(
            store=store).order_by('-sold_at')[:5]

        # 🧮 Total Revenue
        total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or 0

        # 📅 Revenue Last 6 Months
        from django.db.models.functions import TruncMonth
        last_6 = now() - timedelta(days=180)

        revenue_by_month = (
            sales.filter(sold_at__gte=last_6)
            .annotate(month=TruncMonth('sold_at'))
            .values('month')
            .annotate(total=Sum('total_price'))
            .order_by('month')
        )

        # 🔝 Top Products
        top_products = (
            sales.values('product__id', 'product__product_name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )

        return Response({
            'total_revenue': total_revenue,
            'monthly_revenue': revenue_by_month,
            'top_products': top_products,
            'recent_sales': [
                {
                    'id': s.id,
                    'product_name': s.product.product_name,
                    'quantity': s.quantity,
                    'total_price': s.total_price,
                    'refunded': s.refunded,
                    'sold_at': s.sold_at,
                } for s in recent_sales
            ]
        })
