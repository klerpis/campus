from django.urls import path
from .views import (
    VendorListCreateView, VendorDetailView,
    StudentListCreateView, StudentDetailView, UnifiedRegistrationView
)

urlpatterns = [
    # Vendor
    path('vendors/', VendorListCreateView.as_view(),
         name='vendor-list-create'),
    path('vendors/<int:id>/', VendorDetailView.as_view(), name='vendor-detail'),

    # Student
    path('students/', StudentListCreateView.as_view(),
         name='student-list-create'),
    path('students/<int:id>/', StudentDetailView.as_view(),
         name='student-detail'),
    path('register/', UnifiedRegistrationView.as_view(), name='unified-register'),
]
