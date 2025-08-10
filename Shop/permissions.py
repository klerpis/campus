from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    def has_permission(self, request, view):

        return request.user.is_authenticated and (hasattr(request.user, 'vendor') and request.user.vendor.exists())

        # return request.user.is_authenticated and hasattr(request.user, 'campusprofile') and request.user.campusprofile.role == 'vendor'
        # return hasattr(request.user, 'vendor')
