from rest_framework import serializers
from .models import (
    DataPoint, Report, Dashboard, Alert,
    UserBehavior, SalesAnalytics, UserAnalytics,
    ProductAnalytics
)
from accounts.models import User
from django.contrib.contenttypes.models import ContentType

class DataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPoint
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class DashboardSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    
    class Meta:
        model = Dashboard
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class UserBehaviorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all())
    
    class Meta:
        model = UserBehavior
        fields = '__all__'

class SalesAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAnalytics
        fields = '__all__'

class UserAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnalytics
        fields = '__all__'

class ProductAnalyticsSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    
    class Meta:
        model = ProductAnalytics
        fields = '__all__'

class DashboardSummarySerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2)
    sales_trend = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    user_trend = serializers.ListField(child=serializers.IntegerField())
    product_trend = serializers.ListField(child=serializers.IntegerField())
    commission_trend = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2))

class SalesFunnelSerializer(serializers.Serializer):
    views = serializers.IntegerField()
    cart_adds = serializers.IntegerField()
    checkouts = serializers.IntegerField()
    purchases = serializers.IntegerField()
    conversion_rates = serializers.DictField(child=serializers.FloatField())

class UserRetentionSerializer(serializers.Serializer):
    cohort = serializers.DateField()
    total_users = serializers.IntegerField()
    retention_rates = serializers.ListField(child=serializers.FloatField())

class ProductPerformanceSerializer(serializers.Serializer):
    product = serializers.StringRelatedField()
    views = serializers.IntegerField()
    sales = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.FloatField()
    average_rating = serializers.FloatField()

class DistributionAnalyticsSerializer(serializers.Serializer):
    total_distributors = serializers.IntegerField()
    active_distributors = serializers.IntegerField()
    total_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2)
    distribution_trend = serializers.ListField(child=serializers.IntegerField())
    commission_trend = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    top_distributors = serializers.ListField(child=serializers.DictField()) 