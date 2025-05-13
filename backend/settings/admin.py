from django.contrib import admin
from .models import MallSettings, PaymentSettings, ShippingSettings

@admin.register(MallSettings)
class MallSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone', 'updated_at')
    search_fields = ('site_name', 'contact_email', 'contact_phone')
    list_filter = ('created_at', 'updated_at')

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('payment_method', 'is_active', 'merchant_id', 'updated_at')
    list_filter = ('payment_method', 'is_active', 'created_at', 'updated_at')
    search_fields = ('merchant_id', 'app_id')

@admin.register(ShippingSettings)
class ShippingSettingsAdmin(admin.ModelAdmin):
    list_display = ('shipping_method', 'is_active', 'base_fee', 'free_shipping_threshold', 'updated_at')
    list_filter = ('shipping_method', 'is_active', 'created_at', 'updated_at')
    search_fields = ('description',) 