from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        print("🔍 IsAdminUser: request.user =", request.user)
        if request.user and request.user.is_authenticated:
            print("   user id =", request.user.id)
            print("   phone =", getattr(request.user, 'phone', None))
            print("   is_staff =", request.user.is_staff)
            print("   is_superuser =", request.user.is_superuser)
        else:
            print("   пользователь не аутентифицирован")
        return request.user and request.user.is_staff

class TODOAllowAny(BasePermission):
    """TODO: replace with real permission rules."""

    def has_permission(self, request, view):
        return True
