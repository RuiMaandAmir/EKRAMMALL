from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum, Count
from django.conf import settings
import sys
import platform

from orders.models import Order
from accounts.models import DistributorProfile
from products.models import Product

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # 获取今日订单数据
        today_orders = Order.objects.filter(created_at__date=today)
        context['today_orders_count'] = today_orders.count()
        context['today_sales'] = today_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # 获取待处理订单数量
        context['pending_orders_count'] = Order.objects.filter(status='pending').count()
        
        # 获取分销商数量
        context['distributor_count'] = DistributorProfile.objects.count()
        
        # 获取商品总数
        context['product_count'] = Product.objects.count()
        
        # 统计数据
        context['stats'] = [
            ('今日订单', context['today_orders_count']),
            ('今日销售额', f'¥{context["today_sales"]:.2f}'),
            ('待处理订单', context['pending_orders_count']),
            ('分销商数量', context['distributor_count']),
            ('商品总数', context['product_count']),
        ]
        
        # 系统信息
        context['django_version'] = settings.DJANGO_VERSION
        context['python_version'] = f"{platform.python_version()} ({platform.python_implementation()})"
        context['database_name'] = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        context['server_time'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 最近活动
        context['recent_activities'] = self.get_recent_activities()
        
        return context
    
    def get_recent_activities(self):
        activities = []
        
        # 获取最近的订单
        recent_orders = Order.objects.order_by('-created_at')[:5]
        for order in recent_orders:
            activities.append({
                'created_at': order.created_at,
                'content': f'新订单 #{order.order_number} - ¥{order.total_amount}'
            })
        
        # 获取最近的分销商
        recent_distributors = DistributorProfile.objects.order_by('-created_at')[:5]
        for distributor in recent_distributors:
            activities.append({
                'created_at': distributor.created_at,
                'content': f'新分销商 {distributor.user.username}'
            })
        
        # 获取最近添加的商品
        recent_products = Product.objects.order_by('-created_at')[:5]
        for product in recent_products:
            activities.append({
                'created_at': product.created_at,
                'content': f'新商品 {product.name}'
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        return activities[:10]  # 只返回最近10条活动 