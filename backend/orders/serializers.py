from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, Payment, Refund, Withdrawal

class ApplyDistributorCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)

class WithdrawalSerializer(serializers.ModelSerializer):
    """
    提现记录序列化器
    """
    class Meta:
        model = Withdrawal
        fields = ['id', 'distributor', 'amount', 'status', 'bank_name', 'bank_account', 'account_holder',
                 'processed_by', 'processed_at', 'reject_reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'distributor', 'status', 'processed_by', 'processed_at', 'reject_reason',
                           'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'

class CreatePaymentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=['wechat', 'alipay'])
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class CreateRefundSerializer(serializers.Serializer):
    reason = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2) 