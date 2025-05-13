from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import DistributionLink, DistributionLevel, DistributionTeam
from .serializers import (
    DistributionLinkSerializer,
    DistributionLevelSerializer,
    DistributionTeamSerializer,
    DistributorRegistrationSerializer,
    DistributorAuthenticationSerializer,
    CommissionRecordSerializer,
    WithdrawalRecordSerializer,
    WithdrawalRequestSerializer
)
from apps.accounts.models import DistributorProfile, CommissionRecord, WithdrawalRecord
from orders.models import Order

class DistributorRegistrationView(APIView):
    """分销商注册视图"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DistributorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # 创建用户
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            user.phone = serializer.validated_data['phone']
            user.save()

            # 创建分销商档案
            default_level = DistributionLevel.objects.filter(is_default=True).first()
            distributor = DistributorProfile.objects.create(
                user=user,
                level=default_level,
                real_name=serializer.validated_data['real_name'],
                id_card=serializer.validated_data['id_card'],
                bank_name=serializer.validated_data['bank_name'],
                bank_account=serializer.validated_data['bank_account'],
                bank_branch=serializer.validated_data['bank_branch']
            )

            return Response({
                'message': '注册成功，请等待审核',
                'distributor_id': distributor.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DistributorAuthenticationView(APIView):
    """分销商认证视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DistributorAuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            distributor = get_object_or_404(
                DistributorProfile,
                user=request.user
            )
            
            # 更新认证信息
            distributor.real_name = serializer.validated_data['real_name']
            distributor.id_card = serializer.validated_data['id_card']
            distributor.bank_name = serializer.validated_data['bank_name']
            distributor.bank_account = serializer.validated_data['bank_account']
            distributor.bank_branch = serializer.validated_data['bank_branch']
            
            # 保存证件照片
            distributor.id_card_front = serializer.validated_data['id_card_front']
            distributor.id_card_back = serializer.validated_data['id_card_back']
            distributor.bank_card_front = serializer.validated_data['bank_card_front']
            
            distributor.save()
            
            return Response({
                'message': '认证信息提交成功，请等待审核'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DistributionLinkViewSet(viewsets.ModelViewSet):
    """分销链接视图集"""
    serializer_class = DistributionLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        distributor = get_object_or_404(
            DistributorProfile,
            user=self.request.user
        )
        return DistributionLink.objects.filter(distributor=distributor)

    def perform_create(self, serializer):
        distributor = get_object_or_404(
            DistributorProfile,
            user=self.request.user
        )
        serializer.save(distributor=distributor)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """分享链接"""
        link = self.get_object()
        link.increment_click()
        return Response({
            'share_url': link.get_share_url()
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取分销链接统计"""
        distributor = get_object_or_404(
            DistributorProfile,
            user=request.user
        )
        links = DistributionLink.objects.filter(distributor=distributor)
        
        total_clicks = links.aggregate(total=Sum('click_count'))['total'] or 0
        total_orders = links.aggregate(total=Sum('order_count'))['total'] or 0
        total_commission = links.aggregate(total=Sum('total_commission'))['total'] or 0
        
        return Response({
            'total_clicks': total_clicks,
            'total_orders': total_orders,
            'total_commission': total_commission
        })

class DistributionLevelViewSet(viewsets.ModelViewSet):
    """分销商等级视图集"""
    queryset = DistributionLevel.objects.all()
    serializer_class = DistributionLevelSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前用户的分销等级"""
        distributor = get_object_or_404(
            DistributorProfile,
            user=request.user
        )
        return Response(self.get_serializer(distributor.level).data)

class DistributionTeamViewSet(viewsets.ModelViewSet):
    """分销团队视图集"""
    serializer_class = DistributionTeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        distributor = get_object_or_404(
            DistributorProfile,
            user=self.request.user
        )
        return DistributionTeam.objects.filter(
            parent=distributor
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取团队统计"""
        distributor = get_object_or_404(
            DistributorProfile,
            user=request.user
        )
        team = DistributionTeam.objects.filter(parent=distributor)
        
        total_members = team.count()
        total_sales = team.aggregate(
            total=Sum('distributor__total_sales')
        )['total'] or 0
        
        return Response({
            'total_members': total_members,
            'total_sales': total_sales
        })

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """获取团队层级结构"""
        distributor = get_object_or_404(
            DistributorProfile,
            user=request.user
        )
        
        def get_team_tree(parent):
            members = DistributionTeam.objects.filter(parent=parent)
            return [{
                'distributor': self.get_serializer(member).data,
                'children': get_team_tree(member.distributor)
            } for member in members]
        
        return Response(get_team_tree(distributor))

class CommissionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """佣金记录视图集"""
    serializer_class = CommissionRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        distributor = get_object_or_404(
            DistributorProfile,
            user=self.request.user
        )
        return CommissionRecord.objects.filter(distributor=distributor)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取佣金统计"""
        distributor = get_object_or_404(
            DistributorProfile,
            user=request.user
        )
        
        total_commission = distributor.total_commission
        available_commission = distributor.available_commission
        frozen_commission = distributor.frozen_commission
        
        # 获取各状态的佣金记录数量
        status_counts = CommissionRecord.objects.filter(
            distributor=distributor
        ).values('status').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )
        
        return Response({
            'total_commission': total_commission,
            'available_commission': available_commission,
            'frozen_commission': frozen_commission,
            'status_counts': status_counts
        })

class WithdrawalRecordViewSet(viewsets.ModelViewSet):
    """提现记录视图集"""
    serializer_class = WithdrawalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        distributor = get_object_or_404(
            DistributorProfile,
            user=self.request.user
        )
        return WithdrawalRecord.objects.filter(distributor=distributor)

    def create(self, request):
        """申请提现"""
        serializer = WithdrawalRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            distributor = get_object_or_404(
                DistributorProfile,
                user=request.user
            )
            
            # 创建提现记录
            withdrawal = WithdrawalRecord.objects.create(
                distributor=distributor,
                amount=serializer.validated_data['amount'],
                bank_name=distributor.bank_name,
                bank_account=distributor.bank_account,
                bank_branch=distributor.bank_branch
            )
            
            # 冻结佣金
            distributor.withdraw_commission(serializer.validated_data['amount'])
            
            return Response({
                'message': '提现申请已提交，请等待审核',
                'withdrawal_id': withdrawal.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 