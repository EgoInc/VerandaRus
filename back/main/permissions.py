from rest_framework.permissions import BasePermission


class TODOAllowAny(BasePermission):
    """TODO: replace with real permission rules."""

    def has_permission(self, request, view):
        return True
