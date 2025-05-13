from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    只允许管理员进行修改操作，其他用户只能查看
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsAdminOrDistributor(permissions.BasePermission):
    """
    允许管理员和分销商访问
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or hasattr(request.user, 'distributor_profile'))

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    只允许对象的所有者或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user

class IsDistributorOrAdmin(permissions.BasePermission):
    """
    只允许分销商或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return hasattr(request.user, 'distributor_profile') and obj.distributor == request.user.distributor_profile 