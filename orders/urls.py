# urls.py

from django.urls import path
from .views import (
    CartViewSet, WishlistViewSet,
    OrderListCreateView, PaymentCreateView,
    OrderRetrieveView, VendorCompletedOrdersView,
    OrderStatusUpdateView, VendorOrderExportView,
    OrderBulkUpdateView, OrderListView,
)

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

# urlpatterns = router.urls


urlpatterns = [
    # path('cart/', CartListCreateView.as_view(), name='cart'),
    # path('wishlist/', WishlistListCreateView.as_view(), name='wishlist'),
    path('orders/', OrderListCreateView.as_view(), name='order'),
    path('allorders/', OrderListView.as_view(), name='order'),

    path('orders/export/', VendorOrderExportView.as_view(), name='export-orders'),
    path('bulk-update/', OrderBulkUpdateView.as_view(),
         name='bulk-update-orders'),


    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(),
         name='order-status-update'),

    path('orders/<int:pk>/', OrderRetrieveView.as_view(), name='order-detail'),
    path('sales/completed/', VendorCompletedOrdersView.as_view(),
         name='completed-sales'),
    path('payment/', PaymentCreateView.as_view(), name='payment'),
    *router.urls,


]
