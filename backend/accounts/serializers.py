from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import (
    UserProfile, Commission, CommissionHistory,
    DistributorProfile, WithdrawalRecord, CommissionRecord, Notification, MemberLevel
)
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address')
        read_only_fields = ('id',)

class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = ('id', 'user', 'amount', 'status', 'source', 'description', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class CommissionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionHistory
        fields = ('id', 'commission', 'status', 'remark', 'created_at')
        read_only_fields = ('created_at',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "密码不匹配"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError("用户名或密码错误")
        return {'user': user}

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "新密码不匹配"})
        return data

class WechatAuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)

class MemberLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberLevel
        fields = '__all__'

class DistributorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DistributorProfile
        fields = ('id', 'user', 'is_approved', 'total_earnings', 'balance', 'created_at')
        read_only_fields = ('id', 'total_earnings', 'balance', 'created_at')

class CommissionRecordSerializer(serializers.ModelSerializer):
    distributor = DistributorProfileSerializer(read_only=True)
    
    class Meta:
        model = CommissionRecord
        fields = ('id', 'distributor', 'amount', 'type', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')

class WithdrawalRecordSerializer(serializers.ModelSerializer):
    distributor = DistributorProfileSerializer(read_only=True)
    
    class Meta:
        model = WithdrawalRecord
        fields = ('id', 'distributor', 'amount', 'status', 'bank_name', 'bank_account', 'account_holder', 'created_at')
        read_only_fields = ('id', 'created_at')

class DistributorDashboardSerializer(serializers.Serializer):
    total_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    available_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    today_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    this_month_commission = serializers.DecimalField(max_digits=10, decimal_places=2)
    team_size = serializers.IntegerField()
    recent_commissions = CommissionRecordSerializer(many=True)
    recent_orders = serializers.ListField()

class DistributorTeamSerializer(serializers.Serializer):
    team_members = serializers.ListField()
    first_level_count = serializers.IntegerField()
    second_level_count = serializers.IntegerField()
    total_team_commission = serializers.DecimalField(max_digits=10, decimal_places=2)

class WithdrawalApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRecord
        fields = ['amount']
    
    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError("提现金额不能低于1元")
        if value > 20000:
            raise serializers.ValidationError("单笔提现金额不能超过20000元")
        return value
    
    def validate(self, data):
        distributor = self.context['request'].user.distributor_profile
        # 检查余额
        if data['amount'] > distributor.balance:
            raise serializers.ValidationError("提现金额不能超过可用余额")
        # 检查是否有未完成的提现申请
        pending_withdrawals = WithdrawalRecord.objects.filter(
            distributor=distributor,
            status='pending'
        ).count()
        if pending_withdrawals > 0:
            raise serializers.ValidationError("您有未完成的提现申请，请等待处理完成后再申请")
        # 检查每日提现次数限制
        today = timezone.now().date()
        today_withdrawals = WithdrawalRecord.objects.filter(
            distributor=distributor,
            created_at__date=today
        ).count()
        if today_withdrawals >= 3:
            raise serializers.ValidationError("今日提现次数已达上限（3次）")
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'type', 'title', 'content', 'is_read', 'created_at')
        read_only_fields = ('created_at',)