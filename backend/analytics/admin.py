from django.contrib import admin
from .models import (
    SalesAnalytics, UserAnalytics, ProductAnalytics,
    DataPoint, Report, Dashboard, Alert, UserBehavior
)

@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'order_count', 'average_order_value', 'product_count', 'customer_count')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'new_users', 'active_users', 'returning_users', 'churned_users', 'total_users')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'views', 'sales', 'revenue', 'conversion_rate', 'average_rating')
    list_filter = ('date', 'product')
    date_hierarchy = 'date'

@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'timestamp', 'category')
    list_filter = ('name', 'category', 'timestamp')
    search_fields = ('name', 'category')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_by', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'threshold', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'content_type', 'created_at')
    list_filter = ('action', 'content_type', 'created_at')
    search_fields = ('user__username', 'action')
