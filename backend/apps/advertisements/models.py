from django.db import models
from django.utils import timezone

class Advertisement(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('图片', upload_to='advertisements/')
    link_url = models.URLField('链接地址', blank=True, null=True)
    allow_close = models.BooleanField('允许关闭', default=True)
    status = models.BooleanField('状态', default=True)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '广告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.status and self.start_time <= now <= self.end_time 