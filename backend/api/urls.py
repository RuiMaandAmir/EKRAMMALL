from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, UserViewSet, DistributorViewSet
from accounts.views import WithdrawalRecordViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'users', UserViewSet)
router.register(r'distributors', DistributorViewSet)
router.register(r'withdrawals', WithdrawalRecordViewSet, basename='withdrawal')

urlpatterns = [
    path('', include(router.urls)),
] 