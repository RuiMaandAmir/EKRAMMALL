from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from apps.accounts.models import User, DistributorProfile
from orders.models import Order
from products.models import Product

@staff_member_required
def admin_dashboard(request):
    # 获取今日日期范围
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    # 统计数据
    context = {
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_distributors': DistributorProfile.objects.count(),
        'today_sales': Order.objects.filter(
            created_at__range=(today_start, today_end),
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
    }

    return render(request, 'admin/admin/index.html', context) 