from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MallSettingsViewSet, PaymentSettingsViewSet, ShippingSettingsViewSet

router = DefaultRouter()
router.register(r'mall', MallSettingsViewSet, basename='mallsettings')
router.register(r'payment', PaymentSettingsViewSet, basename='paymentsettings')
router.register(r'shipping', ShippingSettingsViewSet, basename='shippingsettings')

urlpatterns = [
    path('', include(router.urls)),
] 