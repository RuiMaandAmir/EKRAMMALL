from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from products.models import Product, Category
from django.utils import timezone

class Coupon(models.Model):
    """
    优惠券模型
    """
    TYPE_CHOICES = (
        ('fixed', _('固定金额')),
        ('percentage', _('百分比')),
    )
    
    code = models.CharField(_('优惠码'), max_length=20, unique=True)
    name = models.CharField(_('名称'), max_length=100)
    description = models.TextField(_('描述'), blank=True, null=True)
    type = models.CharField(_('类型'), max_length=20, choices=TYPE_CHOICES)
    value = models.DecimalField(_('值'), max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(_('最低消费'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)
    
    # 限制条件
    max_uses = models.IntegerField(_('最大使用次数'), default=0)  # 0表示无限制
    used_count = models.IntegerField(_('已使用次数'), default=0)
    one_per_user = models.BooleanField(_('每个用户一次'), default=True)
    
    # 时间限制
    start_date = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_date = models.DateTimeField(_('结束时间'), null=True, blank=True)
    
    # 适用范围
    applicable_to_all = models.BooleanField(_('适用于所有产品'), default=True)
    products = models.ManyToManyField(Product, blank=True, related_name='coupons', verbose_name=_('适用产品'))
    categories = models.ManyToManyField(Category, blank=True, related_name='coupons', verbose_name=_('适用分类'))
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('优惠券')
        verbose_name_plural = _('优惠券')

class UserCoupon(models.Model):
    """
    用户领取的优惠券
    """
    STATUS_CHOICES = (
        ('active', _('有效')),
        ('used', _('已使用')),
        ('expired', _('已过期')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupons', verbose_name=_('用户'))
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons', verbose_name=_('优惠券'))
    status = models.CharField(_('状态'), max_length=20, choices=STATUS_CHOICES, default='active')
    used_at = models.DateTimeField(_('使用时间'), null=True, blank=True)
    acquired_at = models.DateTimeField(_('获取时间'), auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}的{self.coupon.name}"
    
    class Meta:
        verbose_name = _('用户优惠券')
        verbose_name_plural = _('用户优惠券')
        unique_together = ('user', 'coupon')  # 一个用户不能重复领取同一张优惠券

class Flash(models.Model):
    """
    限时抢购活动
    """
    name = models.CharField(_('活动名称'), max_length=100)
    description = models.TextField(_('活动描述'), blank=True, null=True)
    is_active = models.BooleanField(_('是否激活'), default=True)
    start_time = models.DateTimeField(_('开始时间'))
    end_time = models.DateTimeField(_('结束时间'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('限时抢购活动')
        verbose_name_plural = _('限时抢购活动')

class FlashItem(models.Model):
    """
    限时抢购商品
    """
    flash = models.ForeignKey(Flash, on_delete=models.CASCADE, related_name='items', verbose_name=_('限时抢购活动'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='flash_items', verbose_name=_('产品'))
    discount_price = models.DecimalField(_('抢购价'), max_digits=10, decimal_places=2)
    stock_limit = models.IntegerField(_('限购数量'), default=0)  # 0表示不限购
    sold_count = models.IntegerField(_('已售数量'), default=0)
    sort_order = models.IntegerField(_('排序'), default=0)
    
    def __str__(self):
        return f"{self.flash.name}的{self.product.name}"
    
    class Meta:
        verbose_name = _('限时抢购商品')
        verbose_name_plural = _('限时抢购商品')
        unique_together = ('flash', 'product')  # 一个活动中一个商品只能有一个抢购价

class Promotion(models.Model):
    """
    营销活动
    """
    TYPE_CHOICES = (
        ('banner', _('轮播图')),
        ('popup', _('弹窗')),
        ('activity', _('活动页')),
    )
    
    name = models.CharField(_('活动名称'), max_length=100)
    type = models.CharField(_('类型'), max_length=20, choices=TYPE_CHOICES)
    image = models.ImageField(_('图片'), upload_to='promotions/')
    url = models.CharField(_('链接'), max_length=255, blank=True, null=True)
    is_active = models.BooleanField(_('是否激活'), default=True)
    start_date = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_date = models.DateTimeField(_('结束时间'), null=True, blank=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('营销活动')
        verbose_name_plural = _('营销活动')
        ordering = ['sort_order', '-created_at']

class DistributionLink(models.Model):
    """
    分销链接
    """
    distributor = models.ForeignKey('accounts.DistributorProfile', on_delete=models.CASCADE, related_name='distribution_links', verbose_name=_('分销商'))
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='distribution_links', verbose_name=_('产品'))
    code = models.CharField(_('分销码'), max_length=20, unique=True)
    share_count = models.IntegerField(_('分享次数'), default=0)
    click_count = models.IntegerField(_('点击次数'), default=0)
    order_count = models.IntegerField(_('订单数'), default=0)
    total_commission = models.DecimalField(_('总佣金'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            import uuid
            self.code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    @property
    def share_url(self):
        """生成分享链接"""
        return f"{settings.SITE_URL}/share/{self.code}"

    @property
    def qr_code_url(self):
        """生成二维码链接"""
        return f"{settings.SITE_URL}/qr/{self.code}"

    def __str__(self):
        return f"{self.distributor.user.username}的{self.product.name}分销链接"

    class Meta:
        verbose_name = _('分销链接')
        verbose_name_plural = _('分销链接')
        unique_together = ('distributor', 'product')

class DistributionLevel(models.Model):
    """
    分销商等级
    """
    name = models.CharField(_('等级名称'), max_length=50)
    level = models.IntegerField(_('等级'), unique=True)
    min_team_size = models.IntegerField(_('最小团队人数'), default=0)
    min_sales = models.DecimalField(_('最小销售额'), max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField(_('佣金比例'), max_digits=5, decimal_places=2)
    second_level_rate = models.DecimalField(_('二级佣金比例'), max_digits=5, decimal_places=2)
    benefits = models.TextField(_('权益说明'), blank=True, null=True)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    # 新增字段
    min_orders = models.IntegerField(_('最小订单数'), default=0)
    min_commission = models.DecimalField(_('最小佣金'), max_digits=10, decimal_places=2, default=0)
    upgrade_bonus = models.DecimalField(_('升级奖励'), max_digits=10, decimal_places=2, default=0)
    icon = models.CharField(_('等级图标'), max_length=100, blank=True, null=True)
    color = models.CharField(_('等级颜色'), max_length=20, blank=True, null=True)
    description = models.TextField(_('等级描述'), blank=True, null=True)
    privileges = models.JSONField(_('特权列表'), default=dict, blank=True)
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"

    class Meta:
        app_label = 'promotions'
        verbose_name = _('分销商等级')
        verbose_name_plural = _('分销商等级')
        ordering = ['level']

class CouponUsage(models.Model):
    """优惠券使用记录"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages', null=True, blank=True, verbose_name=_('优惠券'))
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('用户'))
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('订单'))
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_('使用时间'))
    
    class Meta:
        verbose_name = _('优惠券使用记录')
        verbose_name_plural = _('优惠券使用记录')
        unique_together = ['coupon', 'order']

class PromotionActivity(models.Model):
    """促销活动"""
    name = models.CharField(max_length=100, verbose_name='活动名称')
    description = models.TextField(verbose_name='活动描述')
    start_date = models.DateTimeField(verbose_name='开始时间')
    end_date = models.DateTimeField(verbose_name='结束时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '促销活动'
        verbose_name_plural = verbose_name

class PromotionProduct(models.Model):
    """促销商品"""
    activity = models.ForeignKey(PromotionActivity, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='促销价')
    stock = models.IntegerField(verbose_name='促销库存')
    sold_count = models.IntegerField(default=0, verbose_name='已售数量')
    
    class Meta:
        verbose_name = '促销商品'
        verbose_name_plural = verbose_name
        unique_together = ['activity', 'product']

class PopupAd(models.Model):
    """
    弹窗广告
    """
    name = models.CharField(_('广告名称'), max_length=100)
    image = models.ImageField(_('广告图片'), upload_to='popup_ads/')
    url = models.CharField(_('跳转链接'), max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(_('开始时间'))
    end_time = models.DateTimeField(_('结束时间'))
    display_duration = models.IntegerField(_('显示时长(秒)'), default=5)
    is_active = models.BooleanField(_('是否激活'), default=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('弹窗广告')
        verbose_name_plural = _('弹窗广告')
        ordering = ['sort_order', '-created_at']
