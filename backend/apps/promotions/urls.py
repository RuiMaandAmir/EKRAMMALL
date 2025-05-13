from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'links', views.DistributionLinkViewSet, basename='distribution-link')
router.register(r'levels', views.DistributionLevelViewSet, basename='distribution-level')
router.register(r'teams', views.DistributionTeamViewSet, basename='distribution-team')
router.register(r'commissions', views.CommissionRecordViewSet, basename='commission-record')
router.register(r'withdrawals', views.WithdrawalRecordViewSet, basename='withdrawal-record')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.DistributorRegistrationView.as_view(), name='distributor-register'),
    path('authenticate/', views.DistributorAuthenticationView.as_view(), name='distributor-authenticate'),
] 