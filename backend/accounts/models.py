from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class MemberLevel(models.Model):
    """会员等级模型"""
    name = models.CharField(_('等级名称'), max_length=50)
    level = models.IntegerField(_('等级'), unique=True)
    points_required = models.IntegerField(_('所需积分'), default=0)
    discount = models.DecimalField(_('折扣率'), max_digits=3, decimal_places=2, default=1.00)
    description = models.TextField(_('等级描述'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        app_label = 'accounts'
        verbose_name = _('会员等级')
        verbose_name_plural = _('会员等级')
        ordering = ['level']

    def __str__(self):
        return f"{self.name} (Level {self.level})"

class User(AbstractUser):
    """
    自定义用户模型，扩展Django的AbstractUser
    """
    phone = models.CharField(_('手机号'), max_length=15, blank=True, null=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    is_distributor = models.BooleanField(_('是否为分销商'), default=True)  # 默认成为分销商
    wechat_openid = models.CharField(_('微信OpenID'), max_length=100, blank=True, null=True, unique=True)
    wechat_unionid = models.CharField(_('微信UnionID'), max_length=100, blank=True, null=True, unique=True)
    member_level = models.ForeignKey(
        MemberLevel,
        verbose_name=_('会员等级'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    points = models.IntegerField(_('积分'), default=0)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 如果是新用户，自动创建分销商资料
        if is_new and self.is_distributor:
            DistributorProfile.objects.get_or_create(
                user=self,
                defaults={
                    'commission_rate': 0.05,  # 默认5%佣金率
                }
            )
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')

class UserProfile(models.Model):
    """
    用户资料
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(_('昵称'), max_length=50, blank=True, null=True)
    bio = models.TextField(_('个人简介'), blank=True, null=True)
    address = models.TextField(_('地址'), blank=True, null=True)
    birthday = models.DateField(_('生日'), blank=True, null=True)
    gender = models.CharField(_('性别'), max_length=10, choices=[('male', '男'), ('female', '女'), ('other', '其他')], blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    # 用户画像数据
    favorite_categories = models.JSONField(_('偏好分类'), default=list, blank=True)
    purchase_frequency = models.IntegerField(_('购买频率'), default=0)
    average_order_value = models.DecimalField(_('平均订单金额'), max_digits=10, decimal_places=2, default=0)
    last_purchase_date = models.DateTimeField(_('最后购买时间'), null=True, blank=True)
    preferred_payment_method = models.CharField(_('偏好支付方式'), max_length=50, blank=True, null=True)
    preferred_delivery_time = models.CharField(_('偏好配送时间'), max_length=50, blank=True, null=True)
    customer_lifetime_value = models.DecimalField(_('客户终身价值'), max_digits=10, decimal_places=2, default=0)
    churn_risk = models.DecimalField(_('流失风险'), max_digits=5, decimal_places=2, default=0)
    user_segments = models.JSONField(_('用户分群'), default=list, blank=True)
    behavior_tags = models.JSONField(_('行为标签'), default=list, blank=True)

    def update_user_profile(self):
        """更新用户画像数据"""
        from django.db.models import Avg, Count, Sum
        from orders.models import Order
        
        # 计算购买频率
        orders = Order.objects.filter(user=self.user)
        if orders.exists():
            self.purchase_frequency = orders.count() / ((timezone.now() - self.created_at).days + 1)
            
            # 计算平均订单金额
            self.average_order_value = orders.aggregate(avg=Avg('total_amount'))['avg']
            
            # 更新最后购买时间
            self.last_purchase_date = orders.latest('created_at').created_at
            
            # 计算客户终身价值
            self.customer_lifetime_value = orders.aggregate(total=Sum('total_amount'))['total']
            
            # 更新偏好分类
            from products.models import Product
            category_counts = {}
            for order in orders:
                for item in order.items.all():
                    category = item.product.category.name
                    category_counts[category] = category_counts.get(category, 0) + item.quantity
            self.favorite_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # 计算流失风险
            days_since_last_purchase = (timezone.now() - self.last_purchase_date).days
            self.churn_risk = min(100, days_since_last_purchase / 30 * 100)
            
            # 更新用户分群
            self.user_segments = self._calculate_user_segments()
            
            # 更新行为标签
            self.behavior_tags = self._calculate_behavior_tags()
            
            self.save()

    def _calculate_user_segments(self):
        """计算用户分群"""
        segments = []
        
        # 基于消费金额分群
        if self.customer_lifetime_value > 10000:
            segments.append('高价值客户')
        elif self.customer_lifetime_value > 5000:
            segments.append('中价值客户')
        else:
            segments.append('普通客户')
            
        # 基于购买频率分群
        if self.purchase_frequency > 0.5:
            segments.append('高频客户')
        elif self.purchase_frequency > 0.2:
            segments.append('中频客户')
        else:
            segments.append('低频客户')
            
        # 基于流失风险分群
        if self.churn_risk > 70:
            segments.append('高风险流失')
        elif self.churn_risk > 30:
            segments.append('中风险流失')
        else:
            segments.append('低风险流失')
            
        return segments

    def _calculate_behavior_tags(self):
        """计算行为标签"""
        tags = []
        
        # 基于购买行为添加标签
        if self.purchase_frequency > 0.5:
            tags.append('忠实客户')
        if self.average_order_value > 1000:
            tags.append('大额消费')
        if self.last_purchase_date and (timezone.now() - self.last_purchase_date).days < 7:
            tags.append('近期活跃')
            
        # 基于偏好分类添加标签
        for category, _ in self.favorite_categories[:3]:
            tags.append(f'偏好{category}')
            
        return tags

    def __str__(self):
        return f"{self.user.username}的个人资料"

    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')

class Commission(models.Model):
    """
    佣金
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(_('金额'), max_digits=10, decimal_places=2)
    status = models.CharField(_('状态'), max_length=20, choices=[
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('paid', '已支付')
    ], default='pending')
    source = models.CharField(_('来源'), max_length=50)
    description = models.TextField(_('描述'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    def __str__(self):
        return f"{self.user.username}的佣金 - {self.amount}"

    class Meta:
        verbose_name = _('佣金')
        verbose_name_plural = _('佣金')

class CommissionHistory(models.Model):
    """
    佣金历史记录
    """
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(_('状态'), max_length=20)
    remark = models.TextField(_('备注'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    def __str__(self):
        return f"{self.commission.user.username}的佣金历史 - {self.status}"

    class Meta:
        verbose_name = _('佣金历史')
        verbose_name_plural = _('佣金历史')
        ordering = ['-created_at']

class DistributorProfile(models.Model):
    """
    分销商资料
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='distributor_profile')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    balance = models.DecimalField(_('佣金余额'), max_digits=10, decimal_places=2, default=0)
    total_earnings = models.DecimalField(_('累计佣金'), max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField(_('佣金比例'), max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 新增字段
    level = models.ForeignKey('promotions.DistributionLevel', on_delete=models.SET_NULL, null=True, blank=True, related_name='distributors', verbose_name=_('分销商等级'))
    total_orders = models.IntegerField(_('总订单数'), default=0)
    total_customers = models.IntegerField(_('总客户数'), default=0)
    last_level_upgrade = models.DateTimeField(_('上次升级时间'), null=True, blank=True)
    next_level_progress = models.JSONField(_('下一等级进度'), default=dict, blank=True)
    is_auto_upgrade = models.BooleanField(_('是否自动升级'), default=True)
    is_approved = models.BooleanField(default=False, verbose_name="是否已审核")
    
    def __str__(self):
        return f"{self.user.username}的分销商账户"
    
    class Meta:
        verbose_name = _('分销商资料')
        verbose_name_plural = _('分销商资料')

class WithdrawalRecord(models.Model):
    """
    提现记录
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('success', '提现成功'),
        ('failed', '提现失败'),
    )
    
    distributor = models.ForeignKey(
        DistributorProfile,
        on_delete=models.CASCADE,
        related_name='withdrawals',
        verbose_name='分销商'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='提现金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 银行卡相关字段
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='银行名称')
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name='银行账号')
    account_holder = models.CharField(max_length=100, blank=True, null=True, verbose_name='开户人姓名')
    
    # 微信支付相关字段
    wechat_openid = models.CharField(max_length=100, null=True, blank=True)
    wechat_transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信支付单号')
    
    # 处理信息
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals',
        verbose_name='处理人'
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    reject_reason = models.TextField(null=True, blank=True, verbose_name='拒绝原因')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    balance_returned = models.BooleanField(default=False, verbose_name='余额已返还')
    
    def __str__(self):
        return f"{self.distributor.user.username} - {self.amount}"
    
    class Meta:
        verbose_name = '提现记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

class CommissionRecord(models.Model):
    """
    佣金记录
    """
    STATUS_CHOICES = (
        ('pending', _('待发放')),
        ('paid', _('已发放')),
        ('cancelled', _('已取消')),
    )
    
    distributor = models.ForeignKey(DistributorProfile, on_delete=models.CASCADE, related_name='commission_records', verbose_name=_('分销商'))
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='commission_records', verbose_name=_('订单'), null=True, blank=True)
    amount = models.DecimalField(_('佣金金额'), max_digits=10, decimal_places=2)
    level = models.IntegerField(_('分销层级'), default=1)  # 1表示一级分销，2表示二级分销
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='pending')
    remark = models.TextField(_('备注'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    paid_at = models.DateTimeField(_('发放时间'), null=True, blank=True)
    
    def __str__(self):
        return f"{self.distributor.user.username}的佣金记录"
    
    class Meta:
        verbose_name = _('佣金记录')
        verbose_name_plural = _('佣金记录')
        ordering = ['-created_at']

class Notification(models.Model):
    """
    通知
    """
    TYPE_CHOICES = (
        ('withdrawal_created', '提现申请已提交'),
        ('withdrawal_approved', '提现申请已批准'),
        ('withdrawal_rejected', '提现申请已拒绝'),
        ('withdrawal_completed', '提现已完成'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='用户'
    )
    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='通知类型'
    )
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的通知 - {self.title}"
