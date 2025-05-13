from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CouponViewSet, UserCouponViewSet,
    FlashViewSet, FlashItemViewSet,
    PromotionViewSet, DistributionLinkViewSet,
    DistributionLevelViewSet, PromotionExportView
)

router = DefaultRouter()
router.register(r'coupons', CouponViewSet)
router.register(r'user-coupons', UserCouponViewSet, basename='user-coupon')
router.register(r'flash-sales', FlashViewSet)
router.register(r'flash-items', FlashItemViewSet)
router.register(r'promotions', PromotionViewSet)
router.register(r'distribution-links', DistributionLinkViewSet)
router.register(r'distribution-levels', DistributionLevelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('export/', PromotionExportView.as_view(), name='promotion-export'),
] 