import os

from rest_framework.permissions import BasePermission


class IsServer(BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_X_API_KEY') and request.META.get('HTTP_X_API_KEY') == os.environ.get('X_API_KEY')


class IsRequiredPermissionSatisfied(BasePermission):
    def has_permission(self, request, view):
        if not request.user and not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        if not hasattr(view, 'required_permissions'):
            return False
        required_permissions = view.required_permissions

        REQUEST_METHODS = {
            'OPTIONS': 'view',
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }

        for perm in required_permissions:
            if REQUEST_METHODS.get(request.method) in perm:
                required_permission = perm
                break

        # Block by default if the request method is not found
        if not required_permission:
            return False
        return request.user.has_perm(required_permission)


class IsRequiredPermissionSatisfiedOrServer(BasePermission):
    def has_permission(self, request, view):
        if IsServer().has_permission(request, view):
            return True
        return IsRequiredPermissionSatisfied().has_permission(request, view)
