from rest_framework import permissions
from accounts.permissions import IsAdminUser

class IsPromotionManager(IsAdminUser):
    """促销管理权限"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm('promotions.manage_promotion')

class IsCouponManager(IsAdminUser):
    """优惠券管理权限"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm('promotions.manage_coupon')

class IsActivityManager(IsAdminUser):
    """促销活动管理权限"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm('promotions.manage_activity')

class CanUseCoupon(permissions.BasePermission):
    """优惠券使用权限"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class CanViewPromotion(permissions.BasePermission):
    """查看促销信息权限"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated 