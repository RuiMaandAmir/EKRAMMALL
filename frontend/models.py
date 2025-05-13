from django.db import models
from django.utils.translation import gettext_lazy as _

class Banner(models.Model):
    name = models.CharField(_('名称'), max_length=100)
    position = models.CharField(_('位置'), max_length=50)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('轮播图')
        verbose_name_plural = _('轮播图')

    def __str__(self):
        return self.name

class BannerItem(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(_('标题'), max_length=100)
    image = models.ImageField(_('图片'), upload_to='banners/')
    link = models.URLField(_('链接'), blank=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)

    class Meta:
        verbose_name = _('轮播图项')
        verbose_name_plural = _('轮播图项')
        ordering = ['sort_order']

    def __str__(self):
        return self.title

class Navigation(models.Model):
    name = models.CharField(_('名称'), max_length=100)
    position = models.CharField(_('位置'), max_length=50)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('导航')
        verbose_name_plural = _('导航')

    def __str__(self):
        return self.name

class NavigationItem(models.Model):
    navigation = models.ForeignKey(Navigation, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(_('标题'), max_length=100)
    link = models.URLField(_('链接'))
    icon = models.CharField(_('图标'), max_length=50, blank=True)
    sort_order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)

    class Meta:
        verbose_name = _('导航项')
        verbose_name_plural = _('导航项')
        ordering = ['sort_order']

    def __str__(self):
        return self.title

class HomeLayout(models.Model):
    name = models.CharField(_('名称'), max_length=100)
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('首页布局')
        verbose_name_plural = _('首页布局')

    def __str__(self):
        return self.name

class LayoutSection(models.Model):
    layout = models.ForeignKey(HomeLayout, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(_('标题'), max_length=100)
    type = models.CharField(_('类型'), max_length=50)
    content = models.JSONField(_('内容'))
    sort_order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否激活'), default=True)

    class Meta:
        verbose_name = _('布局区块')
        verbose_name_plural = _('布局区块')
        ordering = ['sort_order']

    def __str__(self):
        return self.title

class SpecialPage(models.Model):
    title = models.CharField(_('标题'), max_length=100)
    slug = models.SlugField(_('URL标识'), unique=True)
    content = models.TextField(_('内容'))
    is_active = models.BooleanField(_('是否激活'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('专题页面')
        verbose_name_plural = _('专题页面')

    def __str__(self):
        return self.title 