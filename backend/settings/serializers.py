from rest_framework import serializers
from .models import MallSettings, PaymentSettings, ShippingSettings

class MallSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MallSettings
        fields = '__all__'

class PaymentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSettings
        fields = '__all__'

class ShippingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingSettings
        fields = '__all__' 