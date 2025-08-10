from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'student') and request.user.student.exists()


class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'vendor') and request.user.vendor.exists()
