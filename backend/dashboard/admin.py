from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MiniProgramSettings, Advertisement, HomePageSettings, NavigationMenu, AdminLog, ExportRecord

@admin.register(MiniProgramSettings)
class MiniProgramSettingsAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'app_id', 'app_secret', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('app_name', 'app_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active', 'start_time', 'end_time')
    list_filter = ('position', 'is_active')
    search_fields = ('title',)
    date_hierarchy = 'start_time'
    ordering = ('-sort_order', '-created_at')

@admin.register(HomePageSettings)
class HomePageSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_announcement_active', 'updated_at')
    list_filter = ('is_announcement_active',)
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')
    ordering = ('sort_order',)

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'content_type', 'object_id', 'created_at')
    list_filter = ('action', 'content_type', 'created_at')
    search_fields = ('user__username', 'object_id')
    readonly_fields = ('user', 'action', 'content_type', 'object_id', 'created_at')

@admin.register(ExportRecord)
class ExportRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'model_name', 'format', 'file_size', 'created_at')
    list_filter = ('format', 'created_at')
    search_fields = ('user__username', 'model_name')
    readonly_fields = ('user', 'model_name', 'format', 'file_path', 'file_size', 'created_at') 