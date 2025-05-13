from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_time', 'end_time', 'allow_close', 'is_active')
    list_filter = ('status', 'allow_close')
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'image', 'link_url')
        }),
        ('显示设置', {
            'fields': ('status', 'allow_close')
        }),
        ('时间设置', {
            'fields': ('start_time', 'end_time')
        }),
    )
