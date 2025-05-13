from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsDistributor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'distributor_profile')

class IsAdminOrDistributor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or hasattr(request.user, 'distributor_profile'))

class IsAdminOrDistributorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or hasattr(request.user, 'distributor_profile'))

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    自定义权限类，只允许对象的所有者或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有对象
        if request.user.is_staff:
            return True
        
        # 对象所有者可以访问自己的对象
        return obj == request.user 