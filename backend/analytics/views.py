from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    DataPoint, Report, Dashboard, Alert,
    UserBehavior, SalesAnalytics, UserAnalytics,
    ProductAnalytics
)
from .serializers import (
    DataPointSerializer, ReportSerializer, DashboardSerializer,
    AlertSerializer, UserBehaviorSerializer, SalesAnalyticsSerializer,
    UserAnalyticsSerializer, ProductAnalyticsSerializer,
    DashboardSummarySerializer, SalesFunnelSerializer,
    UserRetentionSerializer, ProductPerformanceSerializer,
    DistributionAnalyticsSerializer
)
from accounts.models import DistributorProfile as Distributor

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """获取仪表盘摘要数据"""
        # 获取时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取销售数据
        sales_data = SalesAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_sales=Sum('total_sales'),
            total_orders=Sum('order_count'),
            total_products=Sum('product_count'),
            total_customers=Sum('customer_count')
        )
        
        # 获取用户数据
        user_data = UserAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_users=Sum('total_users'),
            new_users=Sum('new_users'),
            active_users=Sum('active_users')
        )
        
        # 获取分销数据
        distributor_data = Distributor.objects.aggregate(
            total_distributors=Count('id'),
            total_commission=Sum('commission_balance'),
            total_withdrawals=Sum('withdrawn_amount')
        )
        
        # 获取趋势数据
        sales_trend = SalesAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).values_list('total_sales', flat=True)
        
        user_trend = UserAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).values_list('total_users', flat=True)
        
        product_trend = SalesAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).values_list('product_count', flat=True)
        
        commission_trend = Distributor.objects.filter(
            created_at__range=[start_date, end_date]
        ).values_list('commission_balance', flat=True)
        
        data = {
            'total_sales': sales_data['total_sales'] or 0,
            'total_orders': sales_data['total_orders'] or 0,
            'total_users': user_data['total_users'] or 0,
            'total_products': sales_data['total_products'] or 0,
            'total_commission': distributor_data['total_commission'] or 0,
            'total_withdrawals': distributor_data['total_withdrawals'] or 0,
            'sales_trend': list(sales_trend),
            'user_trend': list(user_trend),
            'product_trend': list(product_trend),
            'commission_trend': list(commission_trend)
        }
        
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sales_funnel(self, request):
        """获取销售漏斗数据"""
        # 获取时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取各阶段数据
        views = UserBehavior.objects.filter(
            action='view_product',
            created_at__range=[start_date, end_date]
        ).count()
        
        cart_adds = UserBehavior.objects.filter(
            action='add_to_cart',
            created_at__range=[start_date, end_date]
        ).count()
        
        checkouts = UserBehavior.objects.filter(
            action='checkout',
            created_at__range=[start_date, end_date]
        ).count()
        
        purchases = UserBehavior.objects.filter(
            action='purchase',
            created_at__range=[start_date, end_date]
        ).count()
        
        # 计算转化率
        conversion_rates = {
            'view_to_cart': (cart_adds / views * 100) if views > 0 else 0,
            'cart_to_checkout': (checkouts / cart_adds * 100) if cart_adds > 0 else 0,
            'checkout_to_purchase': (purchases / checkouts * 100) if checkouts > 0 else 0,
            'overall': (purchases / views * 100) if views > 0 else 0
        }
        
        data = {
            'views': views,
            'cart_adds': cart_adds,
            'checkouts': checkouts,
            'purchases': purchases,
            'conversion_rates': conversion_rates
        }
        
        serializer = SalesFunnelSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_retention(self, request):
        """获取用户留存数据"""
        # 获取时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)
        
        # 获取用户数据
        user_data = UserAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # 计算留存率
        retention_data = []
        for data in user_data:
            retention_rates = [
                data.returning_users / data.new_users * 100 if data.new_users > 0 else 0
            ]
            
            retention_data.append({
                'cohort': data.date,
                'total_users': data.total_users,
                'retention_rates': retention_rates
            })
        
        serializer = UserRetentionSerializer(retention_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def product_performance(self, request):
        """获取产品表现数据"""
        # 获取时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取产品数据
        product_data = ProductAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('product')
        
        # 计算产品表现
        performance_data = []
        for data in product_data:
            performance_data.append({
                'product': data.product,
                'views': data.views,
                'sales': data.sales,
                'revenue': data.revenue,
                'conversion_rate': data.conversion_rate,
                'average_rating': data.average_rating
            })
        
        serializer = ProductPerformanceSerializer(performance_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def distribution_analytics(self, request):
        """获取分销分析数据"""
        # 获取时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # 获取分销商数据
        distributor_data = Distributor.objects.all()
        
        # 计算分销数据
        total_distributors = distributor_data.count()
        active_distributors = distributor_data.filter(is_active=True).count()
        total_commission = distributor_data.aggregate(
            total=Sum('commission_balance')
        )['total'] or 0
        total_withdrawals = distributor_data.aggregate(
            total=Sum('withdrawn_amount')
        )['total'] or 0
        
        # 获取趋势数据
        distribution_trend = distributor_data.filter(
            created_at__range=[start_date, end_date]
        ).values_list('id', flat=True)
        
        commission_trend = distributor_data.filter(
            created_at__range=[start_date, end_date]
        ).values_list('commission_balance', flat=True)
        
        # 获取顶级分销商
        top_distributors = distributor_data.order_by(
            '-commission_balance'
        )[:10].values(
            'id', 'user__username', 'commission_balance',
            'total_sales', 'total_orders'
        )
        
        data = {
            'total_distributors': total_distributors,
            'active_distributors': active_distributors,
            'total_commission': total_commission,
            'total_withdrawals': total_withdrawals,
            'distribution_trend': list(distribution_trend),
            'commission_trend': list(commission_trend),
            'top_distributors': list(top_distributors)
        }
        
        serializer = DistributionAnalyticsSerializer(data)
        return Response(serializer.data)

class DataPointViewSet(viewsets.ModelViewSet):
    queryset = DataPoint.objects.all()
    serializer_class = DataPointSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserBehaviorViewSet(viewsets.ModelViewSet):
    queryset = UserBehavior.objects.all()
    serializer_class = UserBehaviorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class SalesAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = SalesAnalytics.objects.all()
    serializer_class = SalesAnalyticsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = UserAnalytics.objects.all()
    serializer_class = UserAnalyticsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class ProductAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = ProductAnalytics.objects.all()
    serializer_class = ProductAnalyticsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
