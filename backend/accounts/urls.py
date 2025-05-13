from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, CommissionViewSet,
    DistributorProfileViewSet, WithdrawalRecordViewSet,
    CommissionRecordViewSet, NotificationViewSet, MemberLevelViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'member-levels', MemberLevelViewSet)
router.register(r'distributors', DistributorProfileViewSet)
router.register(r'commissions', CommissionViewSet, basename='commission')
router.register(r'commission-records', CommissionRecordViewSet)
router.register(r'withdrawals', WithdrawalRecordViewSet, basename='withdrawal')
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('withdrawals/<int:pk>/process/', WithdrawalRecordViewSet.as_view({'post': 'process_withdrawal'}), name='process-withdrawal'),
    path('withdrawals/<int:pk>/reject/', WithdrawalRecordViewSet.as_view({'post': 'reject_withdrawal'}), name='reject-withdrawal'),
] 