from django.db import models
from django.utils.translation import gettext_lazy as _

class MallSettings(models.Model):
    """商城设置"""
    site_name = models.CharField(_('商城名称'), max_length=100)
    site_description = models.TextField(_('商城描述'), blank=True)
    logo = models.ImageField(_('商城Logo'), upload_to='settings/', blank=True)
    favicon = models.ImageField(_('网站图标'), upload_to='settings/', blank=True)
    contact_email = models.EmailField(_('联系邮箱'), blank=True)
    contact_phone = models.CharField(_('联系电话'), max_length=20, blank=True)
    address = models.TextField(_('联系地址'), blank=True)
    business_hours = models.CharField(_('营业时间'), max_length=100, blank=True)
    footer_text = models.TextField(_('页脚文本'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商城设置')
        verbose_name_plural = _('商城设置')

    def __str__(self):
        return self.site_name

class PaymentSettings(models.Model):
    """支付设置"""
    PAYMENT_METHODS = (
        ('wechat', _('微信支付')),
        ('alipay', _('支付宝')),
        ('bank', _('银行转账')),
    )

    payment_method = models.CharField(_('支付方式'), max_length=20, choices=PAYMENT_METHODS)
    is_active = models.BooleanField(_('是否启用'), default=True)
    app_id = models.CharField(_('应用ID'), max_length=100, blank=True)
    merchant_id = models.CharField(_('商户ID'), max_length=100, blank=True)
    api_key = models.CharField(_('API密钥'), max_length=200, blank=True)
    api_secret = models.CharField(_('API密钥'), max_length=200, blank=True)
    notify_url = models.URLField(_('回调地址'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('支付设置')
        verbose_name_plural = _('支付设置')

    def __str__(self):
        return f"{self.get_payment_method_display()} - {'启用' if self.is_active else '禁用'}"

class ShippingSettings(models.Model):
    """物流设置"""
    SHIPPING_METHODS = (
        ('express', _('快递配送')),
        ('self_pickup', _('到店自提')),
        ('local_delivery', _('同城配送')),
    )

    shipping_method = models.CharField(_('配送方式'), max_length=20, choices=SHIPPING_METHODS)
    is_active = models.BooleanField(_('是否启用'), default=True)
    base_fee = models.DecimalField(_('基础运费'), max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(_('免运费门槛'), max_digits=10, decimal_places=2, default=0)
    description = models.TextField(_('配送说明'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('物流设置')
        verbose_name_plural = _('物流设置')

    def __str__(self):
        return f"{self.get_shipping_method_display()} - {'启用' if self.is_active else '禁用'}" 