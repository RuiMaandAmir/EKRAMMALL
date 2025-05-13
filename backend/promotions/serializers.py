from rest_framework import serializers
from .models import (
    Coupon, UserCoupon, Flash, FlashItem, Promotion,
    DistributionLink, DistributionLevel, CouponUsage, PromotionActivity, PromotionProduct
)
from products.serializers import ProductSerializer
from accounts.serializers import DistributorProfileSerializer

class DistributionLinkSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(source='distributor.user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = DistributionLink
        fields = ('id', 'distributor', 'distributor_name', 'product', 'product_name', 'code',
                 'share_count', 'click_count', 'order_count', 'total_commission',
                 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('code', 'share_count', 'click_count', 'order_count',
                          'total_commission', 'created_at', 'updated_at')

class DistributionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionLevel
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('used_count', 'created_at', 'updated_at')

class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'
        read_only_fields = ('used_at',)

class PromotionActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionActivity
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PromotionProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = PromotionProduct
        fields = '__all__'
        read_only_fields = ('sold_count',)

class UserCouponSerializer(serializers.ModelSerializer):
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)
    coupon_value = serializers.DecimalField(source='coupon.value', max_digits=10, decimal_places=2, read_only=True)
    coupon_type = serializers.CharField(source='coupon.type', read_only=True)

    class Meta:
        model = UserCoupon
        fields = ('id', 'user', 'coupon', 'coupon_name', 'coupon_value', 'coupon_type', 'status', 'used_at', 'acquired_at')
        read_only_fields = ('used_at', 'acquired_at')

class FlashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flash
        fields = '__all__'

class FlashItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    original_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = FlashItem
        fields = ('id', 'flash', 'product', 'product_name', 'original_price', 'discount_price', 'stock_limit', 'sold_count', 'sort_order')
        read_only_fields = ('sold_count',)

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__' 