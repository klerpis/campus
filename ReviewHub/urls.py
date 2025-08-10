from django.urls import path
from .views import ReviewListCreateView, ProductReviewListView, VendorReviewListView

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/product/<int:product_id>/',
         ProductReviewListView.as_view(), name='product-review-list'),
    path('vendor-reviews/', VendorReviewListView.as_view(),
         name='vendor-review-list'),



]
