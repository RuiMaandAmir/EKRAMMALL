from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from products.models import Product
from apps.accounts.models import DistributorProfile

class DistributionLink(models.Model):
    """分销链接模型"""
    distributor = models.ForeignKey(
        DistributorProfile,
        on_delete=models.CASCADE,
        related_name='distribution_links',
        verbose_name='分销商'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='distribution_links',
        verbose_name='商品'
    )
    code = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='链接编码'
    )
    is_mall_link = models.BooleanField(
        default=False,
        verbose_name='是否商城链接'
    )
    share_count = models.IntegerField(
        default=0,
        verbose_name='分享次数'
    )
    click_count = models.IntegerField(
        default=0,
        verbose_name='点击次数'
    )
    order_count = models.IntegerField(
        default=0,
        verbose_name='订单数'
    )
    total_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='总佣金'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '分销链接'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['distributor', 'code']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        if self.is_mall_link:
            return f"{self.distributor.user.username}的商城分销链接"
        return f"{self.distributor.user.username}的{self.product.name}分销链接"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(8)
        super().save(*args, **kwargs)

    def get_share_url(self):
        """获取分享链接"""
        if self.is_mall_link:
            return f"https://mall.ekram.com/share/{self.code}"
        return f"https://mall.ekram.com/product/{self.product.id}/share/{self.code}"

    def increment_click(self):
        """增加点击次数"""
        self.click_count += 1
        self.save(update_fields=['click_count'])

    def increment_order(self, amount):
        """增加订单数和佣金"""
        self.order_count += 1
        self.total_commission += amount
        self.save(update_fields=['order_count', 'total_commission'])

class DistributionLevel(models.Model):
    """分销商等级模型"""
    name = models.CharField(
        max_length=50,
        verbose_name='等级名称'
    )
    level = models.IntegerField(
        unique=True,
        verbose_name='等级值'
    )
    first_level_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='一级分销比例(%)'
    )
    second_level_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='二级分销比例(%)'
    )
    upgrade_condition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='升级条件(销售额)'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='是否默认等级'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '分销商等级'
        verbose_name_plural = verbose_name
        ordering = ['level']

    def __str__(self):
        return self.name

class DistributionTeam(models.Model):
    """分销团队模型"""
    distributor = models.ForeignKey(
        DistributorProfile,
        on_delete=models.CASCADE,
        related_name='team_members',
        verbose_name='分销商'
    )
    parent = models.ForeignKey(
        DistributorProfile,
        on_delete=models.CASCADE,
        related_name='subordinates',
        verbose_name='上级分销商',
        null=True,
        blank=True
    )
    level = models.IntegerField(
        default=1,
        verbose_name='分销层级'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '分销团队'
        verbose_name_plural = verbose_name
        unique_together = ['distributor', 'parent']

    def __str__(self):
        return f"{self.distributor.user.username}的团队关系"

    def get_team_size(self):
        """获取团队大小"""
        return DistributionTeam.objects.filter(
            parent=self.distributor
        ).count()

    def get_total_sales(self):
        """获取团队总销售额"""
        from orders.models import Order
        return Order.objects.filter(
            distributor__in=DistributionTeam.objects.filter(
                parent=self.distributor
            ).values_list('distributor', flat=True)
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0 