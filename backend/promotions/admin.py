from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Coupon, UserCoupon, Flash, FlashItem, Promotion,
    DistributionLink, DistributionLevel, PromotionActivity,
    PromotionProduct
)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'value', 'is_active', 'max_uses', 'used_count', 'start_date', 'end_date')
    list_filter = ('is_active', 'type', 'start_date', 'end_date')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('used_count',)
    filter_horizontal = ('products', 'categories')
    fieldsets = (
        (None, {'fields': ('name', 'code', 'description', 'type', 'value', 'is_active')}),
        (_('使用限制'), {'fields': ('min_purchase', 'max_uses', 'used_count', 'one_per_user')}),
        (_('时间限制'), {'fields': ('start_date', 'end_date')}),
        (_('适用范围'), {'fields': ('applicable_to_all', 'products', 'categories')}),
    )

class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'status', 'acquired_at', 'used_at')
    list_filter = ('status', 'acquired_at', 'used_at')
    search_fields = ('user__username', 'user__email', 'coupon__name', 'coupon__code')
    readonly_fields = ('acquired_at',)

class FlashItemInline(admin.TabularInline):
    model = FlashItem
    extra = 1

class FlashAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'start_time', 'end_time', 'created_at')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [FlashItemInline]

class FlashItemAdmin(admin.ModelAdmin):
    list_display = ('flash', 'product', 'discount_price', 'stock_limit', 'sold_count', 'sort_order')
    list_filter = ('flash', 'product')
    search_fields = ('flash__name', 'product__name')

class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'start_date', 'end_date', 'sort_order', 'created_at')
    list_filter = ('is_active', 'type', 'start_date', 'end_date')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

class DistributionLinkAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'product', 'code', 'share_count', 'click_count', 'order_count', 'total_commission', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('distributor__user__username', 'product__name', 'code')
    readonly_fields = ('code', 'share_count', 'click_count', 'order_count', 'total_commission', 'created_at', 'updated_at')

class DistributionLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'min_team_size', 'min_sales', 'commission_rate', 'second_level_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

class PromotionProductInline(admin.TabularInline):
    model = PromotionProduct
    extra = 1

class PromotionActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date', 'created_at')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PromotionProductInline]

class PromotionProductAdmin(admin.ModelAdmin):
    list_display = ('activity', 'product', 'discount_price', 'stock', 'sold_count')
    list_filter = ('activity', 'product')
    search_fields = ('activity__name', 'product__name')

admin.site.register(Coupon, CouponAdmin)
admin.site.register(UserCoupon, UserCouponAdmin)
admin.site.register(Flash, FlashAdmin)
admin.site.register(FlashItem, FlashItemAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(DistributionLink, DistributionLinkAdmin)
admin.site.register(DistributionLevel, DistributionLevelAdmin)
admin.site.register(PromotionActivity, PromotionActivityAdmin)
admin.site.register(PromotionProduct, PromotionProductAdmin)
