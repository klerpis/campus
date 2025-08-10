from django.urls import path
from .views import (SaleListCreateView, StockListView,
                    StockUpdateView, RefundSaleView,
                    VendorAnalyticsView, VendorSaleListView,
                    )

urlpatterns = [
    path('sales/', SaleListCreateView.as_view(), name='sale-list-create'),
    path('stock/', StockListView.as_view(), name='stock-list'),
    path('stock/<int:id>/', StockUpdateView.as_view(), name='stock-update'),
    path('sales/<int:id>/refund/', RefundSaleView.as_view(), name='sale-refund'),
    path('analytics/', VendorAnalyticsView.as_view(),
         name='analytics'),
    path('saleslist/', VendorSaleListView.as_view(), name='vendor-sale-list')


]
