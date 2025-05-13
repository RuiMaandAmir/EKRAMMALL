from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from .models import Order, OrderItem, Cart, Payment, Refund, OrderLog

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at', 'view_details')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def view_details(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.id])
        return format_html('<a href="{}">查看详情</a>', url)
    view_details.short_description = _('订单详情')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('subtotal',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number',)
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')

@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')
