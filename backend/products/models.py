from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """
    商品分类
    """
    name = models.CharField(_('分类名称'), max_length=100)
    slug = models.SlugField(_('URL标识'), max_length=100, unique=True, default=uuid.uuid4)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('父分类'))
    description = models.TextField(_('分类描述'), blank=True)
    image = models.ImageField(_('分类图片'), upload_to='categories/', null=True, blank=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('商品分类')
        verbose_name_plural = _('商品分类')
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug or self.slug == str(uuid.uuid4()):
            self.slug = slugify(self.name)
            # 确保slug唯一性
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/category/{self.slug}/'
    
    def get_breadcrumbs(self):
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': current.get_absolute_url()
            })
            current = current.parent
        return breadcrumbs
    
    def get_products(self):
        return self.products.filter(is_active=True)
    
    def get_children(self):
        return self.children.filter(is_active=True)
    
    def get_descendants(self):
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

class Product(models.Model):
    """
    商品
    """
    name = models.CharField(_('商品名称'), max_length=200)
    slug = models.SlugField(_('URL别名'), max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, verbose_name=_('商品分类'), on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(_('商品描述'))
    price = models.DecimalField(_('价格'), max_digits=10, decimal_places=2)
    original_price = models.DecimalField(_('原价'), max_digits=10, decimal_places=2)
    stock = models.IntegerField(_('库存'), default=0)
    sales = models.IntegerField(_('销量'), default=0)
    is_active = models.BooleanField(_('是否上架'), default=True)
    is_featured = models.BooleanField(_('是否推荐'), default=False)
    allow_distribution = models.BooleanField(_('允许分销'), default=True)
    commission_rate = models.DecimalField(
        _('佣金比例'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    secondary_commission_rate = models.DecimalField(_('二级佣金比例'), max_digits=5, decimal_places=2, default=0.05)  # 5%
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # 生成slug，确保唯一性
            self.slug = slugify(self.name)
            if Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('商品')
        verbose_name_plural = _('商品')
        ordering = ['-created_at']

class ProductImage(models.Model):
    """
    商品图片
    """
    product = models.ForeignKey(Product, verbose_name=_('商品'), related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(_('图片'), upload_to='products/')
    is_primary = models.BooleanField(_('是否主图'), default=False)
    sort_order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - 图片 {self.sort_order}"
    
    class Meta:
        verbose_name = _('商品图片')
        verbose_name_plural = _('商品图片')
        ordering = ['sort_order', 'id']

class ProductSpecification(models.Model):
    """
    商品规格
    """
    product = models.ForeignKey(Product, verbose_name=_('商品'), related_name='specifications', on_delete=models.CASCADE)
    name = models.CharField(_('规格名称'), max_length=100)
    value = models.CharField(_('规格值'), max_length=100)
    price_adjustment = models.DecimalField(_('价格调整'), max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(_('库存'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    class Meta:
        verbose_name = _('商品规格')
        verbose_name_plural = _('商品规格')
        unique_together = ['product', 'name', 'value']

class ProductVariant(models.Model):
    """
    产品变体（如不同颜色、尺寸的SKU）
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_('产品'))
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    price = models.DecimalField(_('价格'), max_digits=10, decimal_places=2)
    stock = models.IntegerField(_('库存'), default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.sku}"
    
    class Meta:
        verbose_name = _('产品变体')
        verbose_name_plural = _('产品变体')

class VariantSpecificationValue(models.Model):
    """
    变体的具体规格值
    """
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='specifications', verbose_name=_('产品变体'))
    specification = models.ForeignKey(ProductSpecification, on_delete=models.CASCADE, verbose_name=_('规格类型'))
    value = models.CharField(_('规格值'), max_length=100)  # 如"红色"、"XL"等
    
    def __str__(self):
        return f"{self.specification.name}: {self.value}"
    
    class Meta:
        verbose_name = _('变体规格值')
        verbose_name_plural = _('变体规格值')
        unique_together = ('variant', 'specification')  # 一个变体的同一规格类型只能有一个值

class ProductReview(models.Model):
    """商品评价"""
    product = models.ForeignKey(Product, verbose_name=_('商品'), related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=models.CASCADE)
    rating = models.IntegerField(_('评分'), validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField(_('评价内容'))
    images = models.JSONField(_('评价图片'), default=list, blank=True)
    is_anonymous = models.BooleanField(_('是否匿名'), default=False)
    is_verified = models.BooleanField(_('是否已购买'), default=False)
    likes = models.IntegerField(_('点赞数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品评价')
        verbose_name_plural = _('商品评价')
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # 一个用户只能评价一次

    def __str__(self):
        return f"{self.product.name} - {self.user.username} - {self.rating}星"

class ReviewReply(models.Model):
    """评价回复"""
    review = models.ForeignKey(ProductReview, verbose_name=_('评价'), related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_('回复用户'), on_delete=models.CASCADE)
    content = models.TextField(_('回复内容'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('评价回复')
        verbose_name_plural = _('评价回复')
        ordering = ['created_at']

    def __str__(self):
        return f"回复 {self.review} - {self.user.username}"
