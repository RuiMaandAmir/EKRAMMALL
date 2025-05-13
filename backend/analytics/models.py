from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class DataPoint(models.Model):
    """
    数据点模型，用于存储各种统计数据
    """
    name = models.CharField(_('指标名称'), max_length=100)
    value = models.FloatField(_('指标值'))
    timestamp = models.DateTimeField(_('时间戳'), default=timezone.now)
    category = models.CharField(_('分类'), max_length=50)
    metadata = models.JSONField(_('元数据'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('数据点')
        verbose_name_plural = _('数据点')
        indexes = [
            models.Index(fields=['name', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} ({self.timestamp})"

class Report(models.Model):
    """
    报表模型
    """
    name = models.CharField(_('报表名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True)
    query = models.TextField(_('查询语句'))
    parameters = models.JSONField(_('参数'), default=dict, blank=True)
    schedule = models.CharField(_('调度'), max_length=100, blank=True)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('报表')
        verbose_name_plural = _('报表')
    
    def __str__(self):
        return self.name

class Dashboard(models.Model):
    """
    仪表盘模型
    """
    name = models.CharField(_('仪表盘名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True)
    layout = models.JSONField(_('布局'), default=dict)
    is_public = models.BooleanField(_('是否公开'), default=False)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('创建者'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('仪表盘')
        verbose_name_plural = _('仪表盘')
    
    def __str__(self):
        return self.name

class Alert(models.Model):
    """
    告警模型
    """
    name = models.CharField(_('告警名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True)
    condition = models.TextField(_('触发条件'))
    threshold = models.FloatField(_('阈值'))
    is_active = models.BooleanField(_('是否激活'), default=True)
    notification_channels = models.JSONField(_('通知渠道'), default=list)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('告警')
        verbose_name_plural = _('告警')
    
    def __str__(self):
        return self.name

class UserBehavior(models.Model):
    """
    用户行为模型
    """
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('用户'))
    action = models.CharField(_('行为'), max_length=50)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    metadata = models.JSONField(_('元数据'), default=dict, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('用户行为')
        verbose_name_plural = _('用户行为')
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action}"

class SalesAnalytics(models.Model):
    """
    销售分析模型
    """
    date = models.DateField(_('日期'))
    total_sales = models.DecimalField(_('总销售额'), max_digits=10, decimal_places=2)
    order_count = models.IntegerField(_('订单数'))
    average_order_value = models.DecimalField(_('平均订单金额'), max_digits=10, decimal_places=2)
    product_count = models.IntegerField(_('商品数'))
    customer_count = models.IntegerField(_('客户数'))
    refund_amount = models.DecimalField(_('退款金额'), max_digits=10, decimal_places=2, default=0)
    refund_count = models.IntegerField(_('退款数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('销售分析')
        verbose_name_plural = _('销售分析')
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"销售分析 - {self.date}"

class UserAnalytics(models.Model):
    """
    用户分析模型
    """
    date = models.DateField(_('日期'))
    new_users = models.IntegerField(_('新增用户'))
    active_users = models.IntegerField(_('活跃用户'))
    returning_users = models.IntegerField(_('回访用户'))
    churned_users = models.IntegerField(_('流失用户'))
    total_users = models.IntegerField(_('总用户数'))
    user_segments = models.JSONField(_('用户分群'), default=dict)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('用户分析')
        verbose_name_plural = _('用户分析')
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"用户分析 - {self.date}"

class ProductAnalytics(models.Model):
    """
    商品分析模型
    """
    date = models.DateField(_('日期'))
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name=_('商品'))
    views = models.IntegerField(_('浏览量'))
    sales = models.IntegerField(_('销量'))
    revenue = models.DecimalField(_('收入'), max_digits=10, decimal_places=2)
    conversion_rate = models.FloatField(_('转化率'))
    average_rating = models.FloatField(_('平均评分'))
    review_count = models.IntegerField(_('评价数'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('商品分析')
        verbose_name_plural = _('商品分析')
        indexes = [
            models.Index(fields=['date', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.date}"
