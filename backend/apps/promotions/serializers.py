from rest_framework import serializers
from .models import DistributionLink, DistributionLevel, DistributionTeam
from accounts.serializers import DistributorProfileSerializer
from products.serializers import ProductSerializer
from apps.accounts.models import DistributorProfile, CommissionRecord, WithdrawalRecord
from django.contrib.auth.models import User

class DistributionLinkSerializer(serializers.ModelSerializer):
    """分销链接序列化器"""
    product = ProductSerializer(read_only=True)
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = DistributionLink
        fields = [
            'id', 'product', 'code', 'is_mall_link',
            'click_count', 'order_count', 'total_commission',
            'created_at', 'updated_at', 'share_url'
        ]
        read_only_fields = [
            'code', 'click_count', 'order_count',
            'total_commission', 'created_at', 'updated_at'
        ]

    def get_share_url(self, obj):
        return obj.get_share_url()

class DistributionLevelSerializer(serializers.ModelSerializer):
    """分销商等级序列化器"""
    class Meta:
        model = DistributionLevel
        fields = [
            'id', 'name', 'level', 'first_level_rate',
            'second_level_rate', 'upgrade_condition',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DistributionTeamSerializer(serializers.ModelSerializer):
    """分销团队序列化器"""
    distributor = DistributorProfileSerializer(read_only=True)
    team_size = serializers.SerializerMethodField()
    total_sales = serializers.SerializerMethodField()

    class Meta:
        model = DistributionTeam
        fields = [
            'id', 'distributor', 'parent', 'level',
            'created_at', 'team_size', 'total_sales'
        ]
        read_only_fields = ['created_at']

    def get_team_size(self, obj):
        return obj.get_team_size()

    def get_total_sales(self, obj):
        return obj.get_total_sales()

class DistributorRegistrationSerializer(serializers.Serializer):
    """分销商注册序列化器"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    real_name = serializers.CharField(max_length=50)
    id_card = serializers.CharField(max_length=18)
    bank_name = serializers.CharField(max_length=100)
    bank_account = serializers.CharField(max_length=50)
    bank_branch = serializers.CharField(max_length=100)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被使用')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('手机号已被使用')
        return value

    def validate_id_card(self, value):
        if DistributorProfile.objects.filter(id_card=value).exists():
            raise serializers.ValidationError('身份证号已被使用')
        return value

class DistributorAuthenticationSerializer(serializers.Serializer):
    """分销商认证序列化器"""
    real_name = serializers.CharField(max_length=50)
    id_card = serializers.CharField(max_length=18)
    bank_name = serializers.CharField(max_length=100)
    bank_account = serializers.CharField(max_length=50)
    bank_branch = serializers.CharField(max_length=100)
    id_card_front = serializers.ImageField()
    id_card_back = serializers.ImageField()
    bank_card_front = serializers.ImageField()

    def validate_id_card(self, value):
        if DistributorProfile.objects.filter(id_card=value).exists():
            raise serializers.ValidationError('身份证号已被使用')
        return value

class CommissionRecordSerializer(serializers.ModelSerializer):
    """佣金记录序列化器"""
    distributor = DistributorProfileSerializer(read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = CommissionRecord
        fields = [
            'id', 'distributor', 'order_number', 'amount',
            'level', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class WithdrawalRecordSerializer(serializers.ModelSerializer):
    """提现记录序列化器"""
    distributor = DistributorProfileSerializer(read_only=True)
    processed_by = serializers.CharField(source='processed_by.username', read_only=True)

    class Meta:
        model = WithdrawalRecord
        fields = [
            'id', 'distributor', 'amount', 'status',
            'bank_name', 'bank_account', 'bank_branch',
            'processed_by', 'processed_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'processed_at']

class WithdrawalRequestSerializer(serializers.Serializer):
    """提现申请序列化器"""
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=100,  # 最小提现金额100元
        error_messages={
            'min_value': '提现金额不能小于100元'
        }
    )

    def validate_amount(self, value):
        distributor = DistributorProfile.objects.get(user=self.context['request'].user)
        if value > distributor.available_commission:
            raise serializers.ValidationError('提现金额不能大于可提现佣金')
        return value 