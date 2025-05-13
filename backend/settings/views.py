from rest_framework import viewsets, permissions
from .models import MallSettings, PaymentSettings, ShippingSettings
from .serializers import MallSettingsSerializer, PaymentSettingsSerializer, ShippingSettingsSerializer

class MallSettingsViewSet(viewsets.ModelViewSet):
    queryset = MallSettings.objects.all()
    serializer_class = MallSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

class PaymentSettingsViewSet(viewsets.ModelViewSet):
    queryset = PaymentSettings.objects.all()
    serializer_class = PaymentSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

class ShippingSettingsViewSet(viewsets.ModelViewSet):
    queryset = ShippingSettings.objects.all()
    serializer_class = ShippingSettingsSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions() 