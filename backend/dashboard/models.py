from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class MiniProgramSettings(models.Model):
    app_name = models.CharField(max_length=100, verbose_name='小程序名称')
    app_id = models.CharField(max_length=100, verbose_name='AppID')
    app_secret = models.CharField(max_length=100, verbose_name='AppSecret')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '小程序设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.app_name

class Advertisement(models.Model):
    """广告管理"""
    title = models.CharField(_('广告标题'), max_length=100)
    image = models.ImageField(_('广告图片'), upload_to='advertisements/')
    link = models.URLField(_('链接地址'), blank=True, null=True)
    start_time = models.DateTimeField(_('开始时间'))
    end_time = models.DateTimeField(_('结束时间'))
    is_active = models.BooleanField(_('是否启用'), default=True)
    position = models.CharField(_('显示位置'), max_length=50, choices=[
        ('home_popup', '首页弹窗'),
        ('home_banner', '首页轮播'),
        ('category_banner', '分类页横幅'),
    ])
    sort_order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('广告管理')
        verbose_name_plural = _('广告管理')
        ordering = ['-sort_order', '-created_at']

    def __str__(self):
        return self.title

class HomePageSettings(models.Model):
    """首页设置"""
    title = models.CharField(_('网站标题'), max_length=100)
    logo = models.ImageField(_('网站Logo'), upload_to='settings/')
    footer_text = models.TextField(_('页脚文本'), blank=True)
    announcement = models.TextField(_('公告内容'), blank=True)
    is_announcement_active = models.BooleanField(_('是否显示公告'), default=False)
    theme_color = models.CharField(_('主题色'), max_length=20, default='#4CAF50')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('首页设置')
        verbose_name_plural = _('首页设置')

    def __str__(self):
        return self.title

class NavigationMenu(models.Model):
    """导航菜单"""
    name = models.CharField(_('菜单名称'), max_length=50)
    url = models.CharField(_('链接地址'), max_length=200)
    icon = models.CharField(_('图标'), max_length=50, blank=True)
    parent = models.ForeignKey('self', verbose_name=_('父级菜单'), 
                              on_delete=models.CASCADE, 
                              null=True, blank=True, 
                              related_name='children')
    sort_order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('导航菜单')
        verbose_name_plural = _('导航菜单')
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name

class AdminLog(models.Model):
    """
    管理员操作日志
    """
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
        ('export', '导出'),
        ('import', '导入'),
        ('other', '其他'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('操作人'))
    action = models.CharField(_('操作类型'), max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('操作对象类型'))
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('操作对象ID'))
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(_('操作对象'), max_length=200, blank=True)
    change_message = models.TextField(_('变更信息'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP地址'), null=True, blank=True)
    created_at = models.DateTimeField(_('操作时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('操作日志')
        verbose_name_plural = _('操作日志')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.object_repr}"

class ExportRecord(models.Model):
    """
    导出记录
    """
    FORMAT_CHOICES = [
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('导出人'))
    model_name = models.CharField(_('模型名称'), max_length=100)
    format = models.CharField(_('导出格式'), max_length=10, choices=FORMAT_CHOICES)
    filters = models.JSONField(_('筛选条件'), default=dict, blank=True)
    file_path = models.CharField(_('文件路径'), max_length=255)
    file_size = models.IntegerField(_('文件大小'), default=0)
    created_at = models.DateTimeField(_('导出时间'), auto_now_add=True)
    is_deleted = models.BooleanField(_('是否已删除'), default=False)

    class Meta:
        verbose_name = _('导出记录')
        verbose_name_plural = _('导出记录')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.model_name} - {self.get_format_display()}" 