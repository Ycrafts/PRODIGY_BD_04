from rest_framework.permissions import BasePermission, SAFE_METHODS

class CustomUserPermission(BasePermission):
    """
    Custom permissions for user access:
    1. Authenticated users can only access their profile (read-only).
    2. Admins can access and modify all users.
    """
    def has_permission(self, request, view):
        if view.action in ['signup', 'login']:
            return True

        if request.user and request.user.is_authenticated:
            if view.action == 'list' and not request.user.is_staff:
                return False
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if request.method in SAFE_METHODS:  
            return obj == request.user

        return False
