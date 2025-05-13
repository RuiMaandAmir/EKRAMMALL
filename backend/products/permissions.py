from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限类：
    - 管理员可以执行所有操作
    - 其他用户只能读取
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff