from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        # print()
        # print(user, user.email, user.vendor, user.student)
        # print()
        token['email'] = user.email
        token['is_vendor'] = hasattr(user, 'vendor') and user.vendor.exists()
        token['is_student'] = hasattr(
            user, 'student') and user.student.exists()
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
