from rest_framework import permissions


class ReadOnlyUserOrIsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.is_staff:
            return True
        return False
