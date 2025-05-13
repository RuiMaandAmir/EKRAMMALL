from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from products.models import Product, ProductVariant
from accounts.models import DistributorProfile, CommissionRecord, User
import uuid
from promotions.models import DistributionLink
import logging

class Order(models.Model):
    """
    订单模型
    """
    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunding', '退款中'),
        ('refunded', '已退款'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('balance', '余额支付'),
    ]
    
    order_number = models.CharField(_('订单号'), max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=models.PROTECT)
    status = models.CharField(_('订单状态'), max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(_('总金额'), max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(_('运费'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('优惠金额'), max_digits=10, decimal_places=2, default=0)
    payment_amount = models.DecimalField(_('支付金额'), max_digits=10, decimal_places=2)
    distributor = models.ForeignKey(DistributorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='distributed_orders', verbose_name=_('分销商'))
    parent_distributor = models.ForeignKey(DistributorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='second_level_orders', verbose_name=_('上级分销商'))
    distribution_code = models.CharField(_('分销码'), max_length=20, null=True, blank=True)
    commission_calculated = models.BooleanField(_('佣金已计算'), default=False)
    
    # 配送信息
    recipient_name = models.CharField(_('收件人姓名'), max_length=100)
    recipient_phone = models.CharField(_('收件人电话'), max_length=20)
    recipient_address = models.TextField(_('收件地址'))
    shipping_method = models.CharField(_('配送方式'), max_length=50, null=True, blank=True)
    tracking_number = models.CharField(_('物流单号'), max_length=100, null=True, blank=True)
    
    # 支付信息
    payment_method = models.CharField(_('支付方式'), max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(_('支付流水号'), max_length=100, null=True, blank=True)
    
    remark = models.TextField(_('备注'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    paid_at = models.DateTimeField(_('支付时间'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('发货时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    
    def calculate_commission(self):
        """
        计算订单佣金
        """
        if self.commission_calculated:
            return
            
        try:
            if self.distributor:
                # 计算一级分销佣金
                commission_amount = self.total_amount * self.distributor.commission_rate
                CommissionRecord.objects.create(
                    distributor=self.distributor,
                    order=self,
                    amount=commission_amount,
                    level=1,
                    status='pending'
                )
                logging.info(f"一级分销佣金计算完成: 订单号={self.order_number}, 分销商={self.distributor.user.username}, 金额={commission_amount}")
                
            if self.parent_distributor:
                # 计算二级分销佣金
                commission_amount = self.total_amount * self.parent_distributor.commission_rate * 0.5  # 二级佣金为一级的一半
                CommissionRecord.objects.create(
                    distributor=self.parent_distributor,
                    order=self,
                    amount=commission_amount,
                    level=2,
                    status='pending'
                )
                logging.info(f"二级分销佣金计算完成: 订单号={self.order_number}, 分销商={self.parent_distributor.user.username}, 金额={commission_amount}")
            
            self.commission_calculated = True
            self.save(update_fields=['commission_calculated'])
            
        except Exception as e:
            logging.error(f"佣金计算失败: 订单号={self.order_number}, 错误={str(e)}")
            raise
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # 如果是新订单且已支付，计算佣金
        if is_new and self.status == 'paid':
            self.calculate_commission()
        
        # 如果订单状态从其他状态变为已支付，计算佣金
        elif not is_new and self.status == 'paid':
            original = Order.objects.get(pk=self.pk)
            if original.status != 'paid':
                self.calculate_commission()
        
        if not self.order_number:
            # 生成订单号，格式：年月日+8位随机数
            import datetime
            prefix = datetime.datetime.now().strftime('%Y%m%d')
            self.order_number = f"{prefix}{uuid.uuid4().hex[:8].upper()}"
            self.save(update_fields=['order_number'])
    
    def __str__(self):
        return self.order_number
    
    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = _('订单')
        ordering = ['-created_at']

class OrderItem(models.Model):
    """
    订单项
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('订单'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('产品'))
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('产品变体'))
    quantity = models.IntegerField(_('数量'), default=1)
    price = models.DecimalField(_('单价'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('小计'), max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # 保存时自动计算小计
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order.order_number}的{self.product.name}"
    
    class Meta:
        verbose_name = _('订单项')
        verbose_name_plural = _('订单项')

class OrderLog(models.Model):
    order = models.ForeignKey(Order, verbose_name=_('订单'), related_name='logs', on_delete=models.CASCADE)
    status = models.CharField(_('状态'), max_length=20, choices=Order.STATUS_CHOICES)
    remark = models.CharField(_('备注'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('订单日志')
        verbose_name_plural = _('订单日志')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

class Cart(models.Model):
    """
    购物车
    """
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    distribution_code = models.CharField(_('分销码'), max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}的购物车"
    
    @property
    def total_items(self):
        return self.items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())
    
    class Meta:
        verbose_name = _('购物车')
        verbose_name_plural = _('购物车')

class CartItem(models.Model):
    """
    购物车项
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('购物车'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('产品'))
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('产品变体'))
    quantity = models.IntegerField(_('数量'), default=1)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    @property
    def price(self):
        return self.variant.price if self.variant else self.product.price
    
    @property
    def subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.cart.user.username}的购物车中的{self.product.name}"
    
    class Meta:
        verbose_name = _('购物车项')
        verbose_name_plural = _('购物车项')
        unique_together = ('cart', 'product', 'variant')  # 同一购物车中同一产品变体只能有一条记录

class Payment(models.Model):
    """
    支付记录
    """
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=Order.PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(_('支付时间'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('支付记录')
        verbose_name_plural = _('支付记录')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.order.order_number} - {self.amount}"

class Refund(models.Model):
    """
    退款记录
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已同意'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
    ]
    
    STATUS_CHOICES = (
        ('pending', _('待处理')),
        ('approved', _('已批准')),
        ('rejected', _('已拒绝')),
        ('completed', _('已完成')),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds', verbose_name=_('订单'))
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds', verbose_name=_('支付记录'))
    amount = models.DecimalField(_('退款金额'), max_digits=10, decimal_places=2)
    status = models.CharField(_('退款状态'), max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(_('退款原因'))
    refund_id = models.CharField(_('退款单号'), max_length=100, blank=True, null=True)
    refund_data = models.JSONField(_('退款数据'), blank=True, null=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    completed_at = models.DateTimeField(_('完成时间'), blank=True, null=True)
    
    def __str__(self):
        return f"{self.order.order_number}的退款记录"
    
    class Meta:
        verbose_name = _('退款记录')
        verbose_name_plural = _('退款记录')
        ordering = ['-created_at']

class Withdrawal(models.Model):
    """
    佣金提现记录
    """
    distributor = models.ForeignKey(
        DistributorProfile,
        on_delete=models.CASCADE,
        related_name='withdrawal_requests',
        verbose_name='分销商'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='提现金额')
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', '待处理'),
            ('approved', '已批准'),
            ('rejected', '已拒绝'),
            ('completed', '已完成')
        ),
        default='pending',
        verbose_name='状态'
    )
    
    # 银行信息
    bank_name = models.CharField(max_length=100, verbose_name='银行名称')
    bank_account = models.CharField(max_length=50, verbose_name='银行账号')
    account_holder = models.CharField(max_length=100, verbose_name='开户人姓名')
    
    # 处理信息
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='处理人'
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    reject_reason = models.TextField(null=True, blank=True, verbose_name='拒绝原因')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.distributor.user.username} - {self.amount}"
    
    class Meta:
        verbose_name = '佣金提现'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
