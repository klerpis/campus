from rest_framework import status
from rest_framework.response import Response
from campusprofile.models import Student, Vendor  # adjust path
from django.contrib.auth.models import User
from .serializers import UnifiedRegistrationSerializer
from rest_framework import generics
from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Vendor, Student
from .serializers import VendorSerializer, StudentSerializer

from .permissions import IsVendor, IsStudent


# Vendor Views
class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vendor.objects.all()[:5]


class VendorDetailView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]


# Student Views
class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]


# class UnifiedRegistrationView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UnifiedRegistrationSerializer

#     def create(self, request, *args, **kwargs):
#         return super().create(request, *args, **kwargs)


class UnifiedRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UnifiedRegistrationSerializer

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        role = validated_data.pop('role')
        password = validated_data.pop('password')

        # print("role1", role)
        # role = serializer._role
        # print("role2", role)

        # Create base user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=password
        )

        # Create linked profile
        if role == 'student':
            Student.objects.create(user=user, email=user.email, role=role)
        elif role == 'vendor':
            Vendor.objects.create(user=user, email=user.email, role=role)

        return user
