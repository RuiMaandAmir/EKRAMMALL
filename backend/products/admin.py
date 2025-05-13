from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Product, Category, ProductImage, ProductVariant,
    ProductSpecification, VariantSpecificationValue, ProductReview, ReviewReply
)
from dashboard.mixins import ExportableModelAdmin

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'sort_order')

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1
    fields = ('name', 'value')

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('specifications', 'sku', 'price', 'stock', 'is_active')

@admin.register(Category)
class CategoryAdmin(ExportableModelAdmin):
    list_display = ('name', 'parent', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order',)

@admin.register(Product)
class ProductAdmin(ExportableModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductSpecificationInline]
    ordering = ('-created_at',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'product')
    search_fields = ('sku', 'product__name')
    fieldsets = (
        ('基本信息', {
            'fields': ('product', 'sku', 'is_active')
        }),
        ('价格库存', {
            'fields': ('price', 'stock')
        }),
        ('规格信息', {
            'fields': ('specifications',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(ProductImage)
class ProductImageAdmin(ExportableModelAdmin):
    list_display = ('product', 'image', 'sort_order', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('product__name',)
    list_editable = ('sort_order', 'is_primary')
    ordering = ('product', 'sort_order')

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(ExportableModelAdmin):
    list_display = ('product', 'name', 'value')
    list_filter = ('product',)
    search_fields = ('product__name', 'name', 'value')
    ordering = ('product', 'name')

class VariantSpecificationValueInline(admin.TabularInline):
    model = VariantSpecificationValue
    extra = 1

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified', 'likes', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_anonymous')
    search_fields = ('product__name', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
    search_fields = ('review__content', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
