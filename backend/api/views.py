from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.utils.encoding import force_str

from products.models import Product
from orders.models import Order
from apps.accounts.models import User, DistributorProfile, CommissionRecord
from .serializers import (
    ProductSerializer, OrderSerializer, UserSerializer,
    DistributorSerializer, CommissionRecordSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsAdminOrDistributor,
    IsOwnerOrAdmin, IsDistributorOrAdmin
)

class ExportMixin:
    def export_csv(self, queryset, filename, fields):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(fields)
        
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field, '')
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(force_str(value))
            writer.writerow(row)
        
        return response

class ProductViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    产品管理API
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        if not request.user.is_staff:
            return Response({'status': 'error', 'message': '没有权限'}, status=403)
        queryset = self.get_queryset()
        fields = ['id', 'name', 'price', 'stock', 'distribution_commission', 'status', 'created_at']
        return self.export_csv(queryset, 'products.csv', fields)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'status': 'error', 'message': '没有权限'}, status=403)
        product = self.get_object()
        product.status = not product.status
        product.save()
        return Response({'status': 'success'})

class OrderViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    订单管理API
    """
    permission_classes = [IsAdminOrDistributor]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        queryset = Order.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(user=self.request.user) |
                Q(distributor=self.request.user.distributor_profile)
            )
        
        search = self.request.query_params.get('search', None)
        status = self.request.query_params.get('status', None)
        
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__username__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        if not request.user.is_staff:
            return Response({'status': 'error', 'message': '没有权限'}, status=403)
        queryset = self.get_queryset()
        fields = ['order_number', 'user__username', 'total_amount', 
                 'commission_amount', 'status', 'created_at']
        return self.export_csv(queryset, 'orders.csv', fields)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response({'status': 'error', 'message': '没有权限'}, status=403)
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'success'})
        return Response({'status': 'error', 'message': '无效的状态'}, status=400)

class UserViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    用户管理API
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.query_params.get('search', None)
        is_distributor = self.request.query_params.get('is_distributor', None)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        if is_distributor is not None:
            queryset = queryset.filter(distributor_profile__isnull=not bool(is_distributor))
            
        return queryset.order_by('-date_joined')
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        fields = ['username', 'email', 'is_active', 'date_joined']
        return self.export_csv(queryset, 'users.csv', fields)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = request.data.get('is_active', not user.is_active)
        user.save()
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def make_distributor(self, request, pk=None):
        user = self.get_object()
        if not hasattr(user, 'distributor_profile'):
            DistributorProfile.objects.create(user=user)
            return Response({'status': 'success'})
        return Response({'status': 'error', 'message': '用户已经是分销商'}, status=400)

class DistributorViewSet(ExportMixin, viewsets.ModelViewSet):
    """
    分销商管理API
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = DistributorProfile.objects.all()
    serializer_class = DistributorSerializer
    
    def get_queryset(self):
        queryset = DistributorProfile.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search)
            )
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        fields = ['user__username', 'user__email', 'balance', 
                 'total_commission', 'order_count', 'created_at']
        return self.export_csv(queryset, 'distributors.csv', fields)
    
    @action(detail=True, methods=['post'])
    def adjust_commission(self, request, pk=None):
        distributor = self.get_object()
        amount = request.data.get('amount')
        remark = request.data.get('remark', '')
        
        if amount:
            try:
                amount = float(amount)
                distributor.balance += amount
                distributor.save()
                
                CommissionRecord.objects.create(
                    distributor=distributor,
                    amount=amount,
                    type='manual_adjustment',
                    remark=remark
                )
                return Response({'status': 'success'})
            except ValueError:
                return Response({'status': 'error', 'message': '无效的金额'}, status=400)
        return Response({'status': 'error', 'message': '金额不能为空'}, status=400)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        distributor = self.get_object()
        distributor.delete()
        return Response({'status': 'success'}) 