from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
import datetime
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from openpyxl import Workbook
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import DistributionLink, DistributionLevel, Coupon, CouponUsage, PromotionActivity, PromotionProduct, UserCoupon, Flash, FlashItem, Promotion
from .serializers import DistributionLinkSerializer, DistributionLevelSerializer, CouponSerializer, CouponUsageSerializer, PromotionActivitySerializer, PromotionProductSerializer, UserCouponSerializer, FlashSerializer, FlashItemSerializer, PromotionSerializer
from products.models import Product
from accounts.models import DistributorProfile, CommissionRecord
from .permissions import (
    IsPromotionManager, IsCouponManager, IsActivityManager,
    CanUseCoupon, CanViewPromotion
)
from .validators import (
    validate_coupon_usage, validate_promotion_activity,
    validate_promotion_product, validate_coupon_data
)
from .exceptions import (
    CouponValidationError, CouponExpiredError, CouponUsedError,
    CouponLimitError, ActivityValidationError, ActivityTimeError,
    ProductStockError, PromotionPriceError
)

class DistributionLinkViewSet(viewsets.ModelViewSet):
    queryset = DistributionLink.objects.all()
    serializer_class = DistributionLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return DistributionLink.objects.all()
        return DistributionLink.objects.filter(distributor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(distributor=self.request.user.distributor_profile)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        link = self.get_object()
        link.share_count += 1
        link.save()
        return Response({'message': '分享成功'})

    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        link = self.get_object()
        link.click_count += 1
        link.save()
        return Response({'message': '点击已记录'})

class DistributionLevelViewSet(viewsets.ModelViewSet):
    queryset = DistributionLevel.objects.all()
    serializer_class = DistributionLevelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return DistributionLevel.objects.all()
        return DistributionLevel.objects.filter(is_active=True)

class GenerateDistributionLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "请提供产品ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "产品不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        distributor = request.user.distributor_profile
        
        # 检查是否已存在分销链接
        link, created = DistributionLink.objects.get_or_create(
            distributor=distributor,
            product=product,
            defaults={'is_active': True}
        )
        
        serializer = DistributionLinkSerializer(link, context={'request': request})
        return Response(serializer.data)

class ShareLinkView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, code, *args, **kwargs):
        try:
            link = DistributionLink.objects.get(code=code, is_active=True)
        except DistributionLink.DoesNotExist:
            return Response({"error": "分享链接不存在或已失效"}, status=status.HTTP_404_NOT_FOUND)
        
        # 更新点击次数
        link.click_count += 1
        link.save()
        
        # 记录分享者信息（如果有）
        if request.user.is_authenticated:
            # 检查是否通过分享链接成为分销商
            if not hasattr(request.user, 'distributor_profile'):
                # 创建分销商资料
                request.user.is_distributor = True
                request.user.save()
                DistributorProfile.objects.create(
                    user=request.user,
                    parent=link.distributor,
                    commission_rate=0.1  # 默认佣金比例
                )
        
        # 返回产品信息
        from products.serializers import ProductSerializer
        product_serializer = ProductSerializer(link.product)
        return Response({
            'product': product_serializer.data,
            'distributor': {
                'id': link.distributor.id,
                'username': link.distributor.user.username
            }
        })

class UpdateDistributionLevelView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        distributor = request.user.distributor_profile
        
        # 计算团队人数
        team_size = DistributorProfile.objects.filter(parent=distributor).count()
        
        # 计算销售额
        today = timezone.now().date()
        month_start = datetime.date(today.year, today.month, 1)
        sales = CommissionRecord.objects.filter(
            distributor=distributor,
            created_at__date__gte=month_start,
            created_at__date__lte=today
        ).aggregate(total_sales=Sum('amount'))['total_sales'] or 0
        
        # 计算订单数
        total_orders = distributor.total_orders
        
        # 计算累计佣金
        total_commission = distributor.total_earnings
        
        # 查找符合条件的等级
        level = DistributionLevel.objects.filter(
            is_active=True,
            min_team_size__lte=team_size,
            min_sales__lte=sales,
            min_orders__lte=total_orders,
            min_commission__lte=total_commission
        ).order_by('-level').first()
        
        if level and (not distributor.level or level.level > distributor.level.level):
            # 更新分销商等级
            distributor.level = level
            distributor.commission_rate = level.commission_rate
            distributor.last_level_upgrade = timezone.now()
            distributor.save()
            
            # 发放升级奖励
            if level.upgrade_bonus > 0:
                CommissionRecord.objects.create(
                    distributor=distributor,
                    amount=level.upgrade_bonus,
                    level=0,  # 0表示升级奖励
                    status='paid',
                    remark=f"升级到{level.name}的奖励"
                )
                distributor.balance += level.upgrade_bonus
                distributor.total_earnings += level.upgrade_bonus
                distributor.save()
            
            return Response({
                "message": "等级更新成功",
                "level": DistributionLevelSerializer(level).data
            })
        
        # 计算下一等级进度
        next_level = DistributionLevel.objects.filter(
            is_active=True,
            level__gt=distributor.level.level if distributor.level else 0
        ).order_by('level').first()
        
        if next_level:
            progress = {
                'team_size': {
                    'current': team_size,
                    'required': next_level.min_team_size,
                    'progress': min(100, team_size / next_level.min_team_size * 100) if next_level.min_team_size > 0 else 100
                },
                'sales': {
                    'current': sales,
                    'required': next_level.min_sales,
                    'progress': min(100, sales / next_level.min_sales * 100) if next_level.min_sales > 0 else 100
                },
                'orders': {
                    'current': total_orders,
                    'required': next_level.min_orders,
                    'progress': min(100, total_orders / next_level.min_orders * 100) if next_level.min_orders > 0 else 100
                },
                'commission': {
                    'current': total_commission,
                    'required': next_level.min_commission,
                    'progress': min(100, total_commission / next_level.min_commission * 100) if next_level.min_commission > 0 else 100
                }
            }
            distributor.next_level_progress = progress
            distributor.save()
        
        return Response({
            "message": "未达到升级条件",
            "current_team_size": team_size,
            "current_sales": sales,
            "current_orders": total_orders,
            "current_commission": total_commission,
            "next_level_progress": distributor.next_level_progress
        })

class DistributionStatisticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'distributor_profile'):
            return Response({"error": "您不是分销商"}, status=status.HTTP_403_FORBIDDEN)
        
        distributor = request.user.distributor_profile
        
        # 获取时间范围
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 构建查询条件
        filters = {'distributor': distributor}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        
        # 统计佣金数据
        commission_stats = CommissionRecord.objects.filter(**filters).aggregate(
            total_commission=Sum('amount'),
            pending_commission=Sum('amount', filter=Q(status='pending')),
            paid_commission=Sum('amount', filter=Q(status='paid')),
            order_count=Count('order', distinct=True)
        )
        
        # 统计分销链接数据
        link_stats = DistributionLink.objects.filter(distributor=distributor).aggregate(
            total_links=Count('id'),
            total_clicks=Sum('click_count'),
            total_orders=Sum('order_count'),
            total_commission=Sum('total_commission')
        )
        
        # 统计团队数据
        team_stats = {
            'direct_members': DistributorProfile.objects.filter(parent=distributor).count(),
            'total_members': DistributorProfile.objects.filter(
                Q(parent=distributor) | Q(parent__parent=distributor)
            ).count()
        }
        
        return Response({
            'commission_stats': commission_stats,
            'link_stats': link_stats,
            'team_stats': team_stats
        })

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        try:
            validate_coupon_data(request.data)
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        coupon = self.get_object()
        user = request.user

        # 检查优惠券是否可用
        if not coupon.is_active:
            return Response({'error': '优惠券已失效'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.start_date and coupon.start_date > timezone.now():
            return Response({'error': '优惠券活动未开始'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.end_date and coupon.end_date < timezone.now():
            return Response({'error': '优惠券活动已结束'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.max_uses > 0 and coupon.used_count >= coupon.max_uses:
            return Response({'error': '优惠券已被领完'}, status=status.HTTP_400_BAD_REQUEST)

        if coupon.one_per_user and UserCoupon.objects.filter(user=user, coupon=coupon).exists():
            return Response({'error': '您已领取过此优惠券'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户优惠券
        user_coupon = UserCoupon.objects.create(user=user, coupon=coupon)
        serializer = UserCouponSerializer(user_coupon)
        return Response(serializer.data)

class UserCouponViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user)

class FlashViewSet(viewsets.ModelViewSet):
    queryset = Flash.objects.all()
    serializer_class = FlashSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Flash.objects.all()
        return Flash.objects.filter(is_active=True)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        flash = self.get_object()
        items = flash.items.all()
        serializer = FlashItemSerializer(items, many=True)
        return Response(serializer.data)

class FlashItemViewSet(viewsets.ModelViewSet):
    queryset = FlashItem.objects.all()
    serializer_class = FlashItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FlashItem.objects.all()
        return FlashItem.objects.filter(flash__is_active=True)

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Promotion.objects.all()
        return Promotion.objects.filter(is_active=True)

def calculate_discount(coupon, order):
    """计算优惠券折扣金额"""
    if coupon.discount_type == 'fixed':
        return min(coupon.discount_value, order.total_amount)
    elif coupon.discount_type == 'percentage':
        return order.total_amount * (coupon.discount_value / 100)
    return 0

class PromotionActivityViewSet(viewsets.ModelViewSet):
    queryset = PromotionActivity.objects.all()
    serializer_class = PromotionActivitySerializer
    permission_classes = [IsActivityManager]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PromotionActivity.objects.all()
        return PromotionActivity.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

    def create(self, request, *args, **kwargs):
        try:
            validate_promotion_activity(request.data)
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[CanViewPromotion])
    def products(self, request, pk=None):
        activity = self.get_object()
        products = activity.products.all()
        serializer = PromotionProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        """添加活动商品"""
        activity = self.get_object()
        product_id = request.data.get('product_id')
        promotion_price = request.data.get('promotion_price')
        stock = request.data.get('stock', 0)
        
        if not product_id or not promotion_price:
            return Response({'error': '请提供商品ID和促销价格'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            product = Product.objects.get(id=product_id)
            validate_promotion_product({
                'product': product,
                'promotion_price': promotion_price,
                'stock': stock
            }, stock)
            
            promotion_product = PromotionProduct.objects.create(
                activity=activity,
                product=product,
                promotion_price=promotion_price,
                stock=stock
            )
            
            return Response(PromotionProductSerializer(promotion_product).data)
            
        except Product.DoesNotExist:
            return Response({'error': '商品不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_product(self, request, pk=None):
        """更新活动商品"""
        activity = self.get_object()
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': '请提供商品ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            promotion_product = PromotionProduct.objects.get(
                activity=activity,
                product_id=product_id
            )
            
            data = request.data.copy()
            data['product'] = product_id
            validate_promotion_product(data, data.get('stock', promotion_product.stock))
            
            serializer = PromotionProductSerializer(
                promotion_product,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except PromotionProduct.DoesNotExist:
            return Response({'error': '活动商品不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        """移除活动商品"""
        activity = self.get_object()
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': '请提供商品ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            promotion_product = PromotionProduct.objects.get(
                activity=activity,
                product_id=product_id
            )
            promotion_product.delete()
            return Response({'message': '商品已从活动中移除'})
            
        except PromotionProduct.DoesNotExist:
            return Response({'error': '活动商品不存在'}, status=status.HTTP_404_NOT_FOUND)

class PromotionProductViewSet(viewsets.ModelViewSet):
    queryset = PromotionProduct.objects.all()
    serializer_class = PromotionProductSerializer
    permission_classes = [IsActivityManager]

    def get_queryset(self):
        activity_id = self.kwargs.get('activity_id')
        if activity_id:
            return self.queryset.filter(activity_id=activity_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        try:
            validate_promotion_product(request.data, request.data.get('stock', 0))
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            validate_promotion_product(request.data, request.data.get('stock', 0))
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """更新商品库存"""
        promotion_product = self.get_object()
        stock = request.data.get('stock')
        
        if stock is None:
            return Response({'error': '请提供库存数量'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            validate_promotion_product({'stock': stock}, stock)
            promotion_product.stock = stock
            promotion_product.save()
            return Response(PromotionProductSerializer(promotion_product).data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """更新促销价格"""
        promotion_product = self.get_object()
        promotion_price = request.data.get('promotion_price')
        
        if promotion_price is None:
            return Response({'error': '请提供促销价格'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            validate_promotion_product({'promotion_price': promotion_price}, promotion_product.stock)
            promotion_product.promotion_price = promotion_price
            promotion_product.save()
            return Response(PromotionProductSerializer(promotion_product).data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PromotionStatsView(APIView):
    permission_classes = [IsPromotionManager]

    def get(self, request):
        try:
            # 获取时间范围
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # 构建查询条件
            filters = {}
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date

            # 统计优惠券数据
            coupon_stats = Coupon.objects.filter(**filters).aggregate(
                total_coupons=Count('id'),
                active_coupons=Count('id', filter=Q(is_active=True)),
                total_used=Sum('used_count'),
                total_discount=Sum('discount_value')
            )

            # 统计活动数据
            activity_stats = PromotionActivity.objects.filter(**filters).aggregate(
                total_activities=Count('id'),
                active_activities=Count('id', filter=Q(is_active=True)),
                total_products=Count('products'),
                total_sales=Sum('products__sold_count')
            )

            # 统计商品数据
            product_stats = PromotionProduct.objects.filter(**filters).aggregate(
                total_products=Count('id'),
                total_stock=Sum('stock'),
                total_sold=Sum('sold_count'),
                total_revenue=Sum('promotion_price') * F('sold_count')
            )

            return Response({
                'coupon_stats': coupon_stats,
                'activity_stats': activity_stats,
                'product_stats': product_stats
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CouponStatsView(APIView):
    permission_classes = [IsPromotionManager]

    def get(self, request):
        try:
            # 获取时间范围
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # 构建查询条件
            filters = {}
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date

            # 按类型统计
            type_stats = Coupon.objects.filter(**filters).values('discount_type').annotate(
                count=Count('id'),
                total_used=Sum('used_count'),
                total_discount=Sum('discount_value')
            )

            # 按状态统计
            status_stats = Coupon.objects.filter(**filters).values('is_active').annotate(
                count=Count('id'),
                total_used=Sum('used_count')
            )

            # 使用趋势
            usage_trend = CouponUsage.objects.filter(**filters).extra(
                select={'date': 'DATE(created_at)'}
            ).values('date').annotate(
                count=Count('id'),
                total_discount=Sum('coupon__discount_value')
            ).order_by('date')

            return Response({
                'type_stats': type_stats,
                'status_stats': status_stats,
                'usage_trend': usage_trend
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivityStatsView(APIView):
    permission_classes = [IsPromotionManager]

    def get(self, request):
        try:
            # 获取时间范围
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # 构建查询条件
            filters = {}
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date

            # 活动效果统计
            activity_stats = PromotionActivity.objects.filter(**filters).annotate(
                total_products=Count('products'),
                total_sold=Sum('products__sold_count'),
                total_revenue=Sum('products__promotion_price') * F('products__sold_count')
            ).values(
                'id', 'name', 'total_products', 'total_sold', 'total_revenue'
            )

            # 商品销售排行
            product_ranking = PromotionProduct.objects.filter(**filters).values(
                'product__name'
            ).annotate(
                sold_count=Sum('sold_count'),
                revenue=Sum('promotion_price') * F('sold_count')
            ).order_by('-sold_count')[:10]

            # 销售趋势
            sales_trend = PromotionProduct.objects.filter(**filters).extra(
                select={'date': 'DATE(created_at)'}
            ).values('date').annotate(
                sold_count=Sum('sold_count'),
                revenue=Sum('promotion_price') * F('sold_count')
            ).order_by('date')

            return Response({
                'activity_stats': activity_stats,
                'product_ranking': product_ranking,
                'sales_trend': sales_trend
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExportPromotionStatsView(APIView):
    permission_classes = [IsPromotionManager]

    def get(self, request):
        try:
            # 获取查询参数
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            activity_id = request.query_params.get('activity')
            product_id = request.query_params.get('product')
            export_type = request.query_params.get('type', 'overview')

            # 构建查询条件
            filters = {}
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date
            if activity_id:
                filters['activity_id'] = activity_id
            if product_id:
                filters['product_id'] = product_id

            if export_type == 'overview':
                # 导出概览数据
                data = self.get_overview_data(filters)
                filename = 'promotion_overview.csv'
            else:
                # 导出详细数据
                data = self.get_detail_data(filters)
                filename = 'promotion_detail.csv'

            # 创建响应
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # 写入CSV数据
            writer = csv.writer(response)
            writer.writerows(data)

            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_overview_data(self, filters):
        """获取概览数据"""
        # 获取优惠券统计数据
        coupon_stats = Coupon.objects.filter(**filters).aggregate(
            total_coupons=Count('id'),
            active_coupons=Count('id', filter=Q(is_active=True)),
            total_used=Sum('used_count'),
            total_discount=Sum('discount_value')
        )

        # 获取活动统计数据
        activity_stats = PromotionActivity.objects.filter(**filters).aggregate(
            total_activities=Count('id'),
            active_activities=Count('id', filter=Q(is_active=True)),
            total_products=Count('products'),
            total_sales=Sum('products__sold_count')
        )

        # 获取商品统计数据
        product_stats = PromotionProduct.objects.filter(**filters).aggregate(
            total_products=Count('id'),
            total_stock=Sum('stock'),
            total_sold=Sum('sold_count'),
            total_revenue=Sum('promotion_price') * F('sold_count')
        )

        # 准备CSV数据
        data = [
            ['促销活动数据统计概览'],
            [''],
            ['优惠券统计'],
            ['总优惠券数', coupon_stats['total_coupons']],
            ['有效优惠券数', coupon_stats['active_coupons']],
            ['使用次数', coupon_stats['total_used']],
            ['总优惠金额', coupon_stats['total_discount']],
            [''],
            ['活动统计'],
            ['总活动数', activity_stats['total_activities']],
            ['进行中活动数', activity_stats['active_activities']],
            ['参与商品数', activity_stats['total_products']],
            ['总销量', activity_stats['total_sales']],
            [''],
            ['商品统计'],
            ['参与商品数', product_stats['total_products']],
            ['总库存', product_stats['total_stock']],
            ['总销量', product_stats['total_sold']],
            ['总销售额', product_stats['total_revenue']]
        ]

        return data

    def get_detail_data(self, filters):
        """获取详细数据"""
        # 获取详细数据
        detail_data = PromotionProduct.objects.filter(**filters).select_related(
            'activity', 'product'
        ).values(
            'created_at',
            'activity__name',
            'product__name',
            'promotion_price',
            'sold_count',
            'stock'
        ).order_by('created_at')

        # 准备CSV数据
        data = [
            ['日期', '活动名称', '商品名称', '促销价格', '销量', '库存']
        ]
        
        for item in detail_data:
            data.append([
                item['created_at'].strftime('%Y-%m-%d'),
                item['activity__name'],
                item['product__name'],
                item['promotion_price'],
                item['sold_count'],
                item['stock']
            ])

        return data

class PromotionExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取时间范围
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # 默认导出最近30天的数据
        if not start_date:
            start_date = (timezone.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = timezone.now().strftime('%Y-%m-%d')

        # 查询数据
        promotions = Promotion.objects.filter(
            created_at__range=[start_date, end_date]
        ).annotate(
            click_count=Count('clicks'),
            conversion_count=Count('conversions')
        )

        # 准备导出数据
        data = []
        for promotion in promotions:
            data.append({
                'id': promotion.id,
                'name': promotion.name,
                'type': promotion.get_type_display(),
                'start_date': promotion.start_date,
                'end_date': promotion.end_date,
                'click_count': promotion.click_count,
                'conversion_count': promotion.conversion_count,
                'conversion_rate': f"{(promotion.conversion_count / promotion.click_count * 100):.2f}%" if promotion.click_count > 0 else "0%"
            })

        return Response(data)
