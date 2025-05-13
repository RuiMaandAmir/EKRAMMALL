from rest_framework import serializers
from products.models import Product
from orders.models import Order, OrderItem
from apps.accounts.models import User, DistributorProfile, CommissionRecord

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 
                 'commission_rate', 'secondary_commission_rate', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("价格必须大于0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("库存不能为负数")
        return value
    
    def validate_commission_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("分销佣金比例必须在0-100之间")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'user_name', 'total_amount',
                 'commission_amount', 'status', 'items', 'created_at']
        read_only_fields = ['order_number', 'created_at']
    
    def validate_status(self, value):
        if value not in dict(Order.STATUS_CHOICES):
            raise serializers.ValidationError("无效的订单状态")
        return value

class UserSerializer(serializers.ModelSerializer):
    distributor_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'distributor_info']
        read_only_fields = ['date_joined']
    
    def get_distributor_info(self, obj):
        if hasattr(obj, 'distributor_profile'):
            return {
                'balance': obj.distributor_profile.balance,
                'total_commission': obj.distributor_profile.total_commission,
                'order_count': obj.distributor_profile.order_count
            }
        return None

class CommissionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRecord
        fields = ['id', 'distributor', 'amount', 'type', 'remark', 'created_at']
        read_only_fields = ['created_at']

class DistributorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    commission_records = CommissionRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = DistributorProfile
        fields = ['id', 'user', 'balance', 'total_commission', 
                 'order_count', 'created_at', 'commission_records']
        read_only_fields = ['created_at'] 