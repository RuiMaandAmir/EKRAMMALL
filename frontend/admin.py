from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Banner, Navigation, HomeLayout, SpecialPage,
    BannerItem, NavigationItem, LayoutSection
)

class BannerItemInline(admin.TabularInline):
    model = BannerItem
    extra = 1
    fields = ('title', 'image', 'link', 'sort_order', 'is_active')

class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'created_at')
    list_filter = ('position', 'is_active', 'created_at')
    search_fields = ('name',)
    inlines = [BannerItemInline]

class NavigationItemInline(admin.TabularInline):
    model = NavigationItem
    extra = 1
    fields = ('title', 'link', 'icon', 'sort_order', 'is_active')

class NavigationAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'created_at')
    list_filter = ('position', 'is_active', 'created_at')
    search_fields = ('name',)
    inlines = [NavigationItemInline]

class LayoutSectionInline(admin.TabularInline):
    model = LayoutSection
    extra = 1
    fields = ('title', 'type', 'content', 'sort_order', 'is_active')

class HomeLayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    inlines = [LayoutSectionInline]

class SpecialPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Banner, BannerAdmin)
admin.site.register(Navigation, NavigationAdmin)
admin.site.register(HomeLayout, HomeLayoutAdmin)
admin.site.register(SpecialPage, SpecialPageAdmin) 