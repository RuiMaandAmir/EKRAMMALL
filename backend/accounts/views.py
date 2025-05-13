from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.utils import timezone
import datetime
from django.db import models, transaction
from rest_framework import serializers
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Sum, Count, Q
from django.conf import settings
from decimal import Decimal

from .models import User, DistributorProfile, WithdrawalRecord, CommissionRecord, UserProfile, MemberLevel, Notification
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer, 
    ChangePasswordSerializer, WechatAuthSerializer, DistributorProfileSerializer,
    WithdrawalRecordSerializer, CommissionRecordSerializer, DistributorDashboardSerializer,
    DistributorTeamSerializer, WithdrawalApplySerializer, UserProfileSerializer,
    MemberLevelSerializer, NotificationSerializer
)
from orders.models import Withdrawal
from orders.serializers import WithdrawalSerializer
from orders.models import Order
from orders.serializers import OrderSerializer
from promotions.models import DistributionLink
from .filters import WithdrawalRecordFilter, CommissionRecordFilter
from .permissions import IsOwnerOrAdmin

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me' and request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            serializer = self.get_serializer(user)
            return Response({
                'token': token.key,
                'user': serializer.data
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '已成功退出'})

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证旧密码
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "旧密码不正确"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "密码修改成功"})

class WechatAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = WechatAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 这里应该调用微信API进行验证，并获取用户信息
        # 由于是模拟，我们直接返回成功
        
        return Response({
            "message": "微信认证成功",
            "user": {
                "id": 1,
                "username": "wechat_user",
                "is_distributor": False
            }
        })

class DistributorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DistributorProfile.objects.all()
    serializer_class = DistributorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return DistributorProfile.objects.all()
        if self.request.user.is_distributor:
            return DistributorProfile.objects.filter(user=self.request.user)
        return DistributorProfile.objects.none()

class WithdrawalRecordViewSet(viewsets.ModelViewSet):
    """
    提现记录视图集
    """
    serializer_class = WithdrawalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return WithdrawalRecord.objects.all()
        return WithdrawalRecord.objects.filter(distributor__user=user)
    
    def perform_create(self, serializer):
        """创建提现记录"""
        # 获取分销商信息
        distributor = self.request.user.distributor_profile
        distributor.refresh_from_db()
        
        # 获取提现金额
        amount = Decimal(str(serializer.validated_data['amount']))
        
        # 验证提现金额
        if amount < Decimal('10.00'):
            raise serializers.ValidationError({'amount': '提现金额不能小于10元'})
        if amount > Decimal('20000.00'):
            raise serializers.ValidationError({'amount': '单次提现金额不能超过20000元'})
        if amount > distributor.balance:
            raise serializers.ValidationError({'amount': '余额不足'})
        
        # 创建提现记录
        withdrawal = serializer.save(
            distributor=distributor,
            status='pending',
            bank_name=serializer.validated_data.get('bank_name', ''),
            bank_account=serializer.validated_data.get('bank_account', ''),
            account_holder=serializer.validated_data.get('account_holder', '')
        )
        
        # 冻结余额
        distributor.balance -= amount
        distributor.save()
        
        # 创建通知
        Notification.objects.create(
            user=distributor.user,
            type='withdrawal_created',
            title='提现申请已提交',
            content=f'您的提现申请已提交，金额：{amount}元'
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({'error': '只能处理待处理的提现申请'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal.status = 'approved'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        return Response({'message': '提现申请已批准'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != 'pending':
            return Response({'error': '只能拒绝待处理的提现申请'}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get('reason')
        if not reason:
            return Response({'error': '请提供拒绝原因'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal.status = 'rejected'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.reject_reason = reason
        withdrawal.save()
        # 只有余额小于初始值时才返还
        distributor = withdrawal.distributor
        if distributor.balance < Decimal('1000.00'):
            distributor.balance += withdrawal.amount
            distributor.save()
        return Response({'message': '提现申请已拒绝'})

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        withdrawal = self.get_object()
        if withdrawal.status != 'approved':
            return Response({'error': '只能完成已批准的提现'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal.status = 'completed'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        return Response({'message': '提现已完成'})

    def process_withdrawal(self, request, pk=None):
        """处理提现申请"""
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            return Response({'error': '只能处理待处理的提现申请'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 调用微信支付API
            from orders.utils.wechat_pay import WechatPay
            wechat_pay = WechatPay()
            result = wechat_pay.transfer_to_balance(
                openid=withdrawal.wechat_openid,
                amount=int(withdrawal.amount * 100),  # 转换为分
                desc=f'佣金提现-{withdrawal.distributor.user.username}'
            )
            
            if result.get('result_code') == 'SUCCESS':
                withdrawal.status = 'success'
                withdrawal.wechat_transaction_id = result.get('payment_no')
                withdrawal.processed_by = request.user
                withdrawal.processed_at = timezone.now()
                withdrawal.save()
                
                # 创建成功通知
                Notification.objects.create(
                    user=withdrawal.distributor.user,
                    type='withdrawal_completed',
                    title='提现已完成',
                    content=f'您的提现申请已处理完成，金额：{withdrawal.amount}元'
                )
                
                return Response({'message': '提现处理成功'})
            else:
                withdrawal.status = 'failed'
                withdrawal.processed_by = request.user
                withdrawal.processed_at = timezone.now()
                withdrawal.reject_reason = result.get('err_code_des')
                withdrawal.save()
                
                # 返还余额
                distributor = withdrawal.distributor
                distributor.balance += withdrawal.amount
                distributor.save()
                
                # 创建失败通知
                Notification.objects.create(
                    user=withdrawal.distributor.user,
                    type='withdrawal_failed',
                    title='提现失败',
                    content=f'您的提现申请处理失败，原因：{result.get("err_code_des")}'
                )
                
                return Response({'error': '提现处理失败'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            withdrawal.status = 'failed'
            withdrawal.processed_by = request.user
            withdrawal.processed_at = timezone.now()
            withdrawal.reject_reason = str(e)
            withdrawal.save()
            
            # 返还余额
            distributor = withdrawal.distributor
            distributor.balance += withdrawal.amount
            distributor.save()
            
            # 创建失败通知
            Notification.objects.create(
                user=withdrawal.distributor.user,
                type='withdrawal_failed',
                title='提现失败',
                content=f'您的提现申请处理失败，原因：{str(e)}'
            )
            
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def reject_withdrawal(self, request, pk=None):
        """拒绝提现申请"""
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            return Response({'error': '只能拒绝待处理的提现申请'}, status=status.HTTP_400_BAD_REQUEST)
            
        reason = request.data.get('reason')
        if not reason:
            return Response({'error': '请提供拒绝原因'}, status=status.HTTP_400_BAD_REQUEST)
            
        withdrawal.status = 'failed'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.reject_reason = reason
        withdrawal.save()
        
        # 返还余额
        distributor = withdrawal.distributor
        distributor.balance += withdrawal.amount
        distributor.save()
        
        # 创建拒绝通知
        Notification.objects.create(
            user=withdrawal.distributor.user,
            type='withdrawal_rejected',
            title='提现申请已拒绝',
            content=f'您的提现申请已被拒绝，原因：{reason}'
        )
        
        return Response({'message': '提现申请已拒绝'})

class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommissionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return CommissionRecord.objects.all()
        if hasattr(self.request.user, 'distributor_profile'):
            return CommissionRecord.objects.filter(distributor=self.request.user.distributor_profile)
        return CommissionRecord.objects.none()

class DistributorProfileViewSet(viewsets.ModelViewSet):
    queryset = DistributorProfile.objects.all()
    serializer_class = DistributorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DistributorProfile.objects.filter(user=self.request.user)

class BecomeDistributorView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您已经是分销商"}, status=status.HTTP_400_BAD_REQUEST)
        
        parent_id = request.data.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = DistributorProfile.objects.get(id=parent_id)
            except DistributorProfile.DoesNotExist:
                return Response({"error": "上级分销商不存在"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            distributor = DistributorProfile.objects.create(
                user=request.user,
                parent=parent,
                name=request.data.get('name', request.user.username),
                phone=request.data.get('phone', ''),
                wechat=request.data.get('wechat', '')
            )
        
        serializer = DistributorProfileSerializer(distributor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DistributorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        distributor = request.user.distributor_profile
        
        # 计算今天的佣金
        today = timezone.now().date()
        today_commission = CommissionRecord.objects.filter(
            distributor=distributor,
            created_at__date=today
        ).aggregate(today_sum=models.Sum('amount'))['today_sum'] or 0
        
        # 计算本月的佣金
        month_start = datetime.date(today.year, today.month, 1)
        month_commission = CommissionRecord.objects.filter(
            distributor=distributor,
            created_at__date__gte=month_start,
            created_at__date__lte=today
        ).aggregate(month_sum=models.Sum('amount'))['month_sum'] or 0
        
        # 获取最近的佣金记录
        recent_commissions = CommissionRecord.objects.filter(
            distributor=distributor
        ).order_by('-created_at')[:5]
        
        # 获取团队大小
        team_size = DistributorProfile.objects.filter(parent=distributor).count()
        
        # 构建响应
        data = {
            'total_commission': distributor.total_earnings,
            'available_balance': distributor.balance,
            'today_commission': today_commission,
            'this_month_commission': month_commission,
            'team_size': team_size,
            'recent_commissions': CommissionRecordSerializer(recent_commissions, many=True).data,
            'recent_orders': []  # 这里需要从订单模型中获取数据
        }
        
        return Response(data)

class DistributorTeamView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        distributor = request.user.distributor_profile
        
        # 获取一级团队成员
        first_level = DistributorProfile.objects.filter(parent=distributor)
        first_level_serialized = DistributorProfileSerializer(first_level, many=True).data
        
        # 获取二级团队成员
        second_level_ids = first_level.values_list('id', flat=True)
        second_level = DistributorProfile.objects.filter(parent__in=second_level_ids)
        second_level_serialized = DistributorProfileSerializer(second_level, many=True).data
        
        # 团队数据
        data = {
            'team_members': first_level_serialized + second_level_serialized,
            'first_level_count': len(first_level_serialized),
            'second_level_count': len(second_level_serialized),
            'total_team_commission': 0  # 这里需要计算团队佣金
        }
        
        return Response(data)

class ApplyWithdrawalView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        distributor = request.user.distributor_profile
        serializer = WithdrawalApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        
        # 检查余额是否充足
        if amount > distributor.balance:
            return Response({"error": "余额不足"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建提现记录
        withdrawal = WithdrawalRecord.objects.create(
            distributor=distributor,
            amount=amount,
            status='pending'
        )
        
        # 扣减余额
        distributor.balance -= amount
        distributor.save()
        
        return Response({
            "message": "提现申请已提交",
            "withdrawal": WithdrawalRecordSerializer(withdrawal).data
        })

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            user = serializer.save()
            Token.objects.create(user=user)

class RefreshTokenView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        return Response({'token': token.key})

class LogoutView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserListView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

class UserProfileViewSet(viewsets.ModelViewSet):
    """用户资料视图集"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_object(self):
        return self.request.user.profile

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

class MemberLevelListView(viewsets.ModelViewSet):
    queryset = MemberLevel.objects.all()
    serializer_class = MemberLevelSerializer
    permission_classes = [permissions.IsAdminUser]

class MemberLevelDetailView(viewsets.ModelViewSet):
    queryset = MemberLevel.objects.all()
    serializer_class = MemberLevelSerializer
    permission_classes = [permissions.IsAdminUser]

class DistributorProfileViewSet(viewsets.ModelViewSet):
    queryset = DistributorProfile.objects.all()
    serializer_class = DistributorProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        distributor = self.get_object()
        distributor.is_approved = True
        distributor.save()
        return Response({'status': 'distributor approved'})

class CommissionRecordViewSet(viewsets.ModelViewSet):
    queryset = CommissionRecord.objects.all()
    serializer_class = CommissionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CommissionRecord.objects.all()
        return CommissionRecord.objects.filter(distributor__user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MemberLevelViewSet(viewsets.ModelViewSet):
    """会员等级视图集"""
    queryset = MemberLevel.objects.all()
    serializer_class = MemberLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
