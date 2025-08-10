from .views import StoreViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ProductListCreateView, ProductDetailView, StoreTypesListView,
    CategoryListView, ApprovedStoreListView, StoreDetailView,
)

router = DefaultRouter()
router.register(r'store', StoreViewSet, basename='store')


urlpatterns = [

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('stores-types/', StoreTypesListView.as_view(), name='store-types'),
    path('stores/', ApprovedStoreListView.as_view(), name='approved-store-list'),
    path('stores/<int:id>/', StoreDetailView.as_view(), name='store-detail'),

    *router.urls,
]
