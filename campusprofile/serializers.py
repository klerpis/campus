from campusprofile.models import Student, Vendor  # adjust path if needed
from Shop.models import Store, StoreType
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Vendor, Student
from Shop.models import Store  # because Vendor has a OneToOneField to Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'store_name', 'address', 'store_type']


class VendorSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Vendor
        fields = ['id', 'first_name', 'last_name',
                  'phonenumber', 'email', 'store']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'phonenumber', 'email']


class UnifiedRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[('student', 'Student'), ('vendor', 'Vendor')],
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Extract role separately before saving user
        role = validated_data.pop('role')
        self._role = role  # temporarily stash for use in view
        return super().create(validated_data)
