from rest_framework.permissions import BasePermission, SAFE_METHODS

class CustomUserPermission(BasePermission):
    """
    Custom permissions for user access:
    1. Authenticated users can only access their profile (read-only).
    2. Admins can access and modify all users.
    """
    def has_permission(self, request, view):
        # Allow signup and login for unauthenticated users
        if view.action in ['signup', 'login']:
            return True

        if request.user and request.user.is_authenticated:
            # Restrict the `list` action to admins only
            if view.action == 'list' and not request.user.is_staff:
                return False
            return True

        return False
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff:
            return True

        # Users can only read their own profile
        if request.method in SAFE_METHODS:  # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
            return obj == request.user

        # Deny write access to non-admins
        return False
