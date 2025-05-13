from django.contrib import admin
from .models import DistributionLink, DistributionLevel, DistributionTeam
from apps.accounts.models import DistributorProfile, CommissionRecord, WithdrawalRecord
from django.utils import timezone
from django.utils.html import format_html

@admin.register(DistributorProfile)
class DistributorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'real_name', 'level', 'total_sales', 'total_commission', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'level']
    search_fields = ['user__username', 'real_name', 'id_card', 'phone']
    readonly_fields = ['total_sales', 'total_commission', 'available_commission', 'frozen_commission', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'real_name', 'phone', 'id_card')
        }),
        ('认证信息', {
            'fields': ('is_verified', 'is_active', 'id_card_front', 'id_card_back')
        }),
        ('分销信息', {
            'fields': ('level', 'parent', 'total_sales', 'total_commission', 'available_commission', 'frozen_commission')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )
    actions = ['verify_distributors', 'unverify_distributors', 'activate_distributors', 'deactivate_distributors']

    def verify_distributors(self, request, queryset):
        queryset.update(is_verified=True)
    verify_distributors.short_description = '批量认证选中的分销商'

    def unverify_distributors(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_distributors.short_description = '批量取消认证选中的分销商'

    def activate_distributors(self, request, queryset):
        queryset.update(is_active=True)
    activate_distributors.short_description = '批量启用选中的分销商'

    def deactivate_distributors(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_distributors.short_description = '批量禁用选中的分销商'

@admin.register(DistributionLevel)
class DistributionLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'first_level_rate', 'second_level_rate', 'upgrade_condition', 'is_default']
    list_filter = ['is_default']
    search_fields = ['name']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'level', 'is_default')
        }),
        ('分销比例', {
            'fields': ('first_level_rate', 'second_level_rate')
        }),
        ('升级条件', {
            'fields': ('upgrade_condition',)
        })
    )

@admin.register(DistributionLink)
class DistributionLinkAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'product', 'code', 'click_count', 'order_count', 'total_commission', 'created_at']
    list_filter = ['is_mall_link']
    search_fields = ['distributor__user__username', 'product__name', 'code']
    readonly_fields = ['click_count', 'order_count', 'total_commission', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('distributor', 'product', 'code', 'is_mall_link')
        }),
        ('统计数据', {
            'fields': ('click_count', 'order_count', 'total_commission')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(DistributionTeam)
class DistributionTeamAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'parent', 'level', 'created_at']
    list_filter = ['level']
    search_fields = ['distributor__user__username', 'parent__user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('团队信息', {
            'fields': ('distributor', 'parent', 'level')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        })
    )

@admin.register(CommissionRecord)
class CommissionRecordAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'order_number', 'amount', 'level', 'status', 'created_at']
    list_filter = ['status', 'level']
    search_fields = ['distributor__user__username', 'order__order_number']
    readonly_fields = ['distributor', 'order', 'amount', 'level', 'status', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('distributor', 'order', 'amount', 'level')
        }),
        ('状态信息', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )
    actions = ['freeze_commissions', 'unfreeze_commissions', 'cancel_commissions']

    def freeze_commissions(self, request, queryset):
        queryset.filter(status='pending').update(status='frozen')
    freeze_commissions.short_description = '批量冻结选中的佣金'

    def unfreeze_commissions(self, request, queryset):
        queryset.filter(status='frozen').update(status='available')
    unfreeze_commissions.short_description = '批量解冻选中的佣金'

    def cancel_commissions(self, request, queryset):
        queryset.filter(status__in=['pending', 'frozen']).update(status='cancelled')
    cancel_commissions.short_description = '批量取消选中的佣金'

@admin.register(WithdrawalRecord)
class WithdrawalRecordAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'amount', 'wechat_nickname', 'status', 'created_at', 'processed_at', 'status_tag']
    list_filter = ['status']
    search_fields = ['distributor__user__username', 'wechat_nickname']
    readonly_fields = ['distributor', 'amount', 'wechat_nickname', 'created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('distributor', 'amount', 'wechat_nickname')
        }),
        ('状态信息', {
            'fields': ('status', 'processed_by', 'processed_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        })
    )
    actions = ['approve_withdrawals', 'reject_withdrawals']

    def status_tag(self, obj):
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger'
        }
        status_texts = {
            'pending': '待处理',
            'approved': '已通过',
            'rejected': '已拒绝'
        }
        return format_html(
            '<span class="el-tag el-tag--{}">{}</span>',
            status_colors.get(obj.status, 'info'),
            status_texts.get(obj.status, obj.status)
        )
    status_tag.short_description = '状态'

    def approve_withdrawals(self, request, queryset):
        queryset.filter(status='pending').update(
            status='approved',
            processed_by=request.user,
            processed_at=timezone.now()
        )
    approve_withdrawals.short_description = '批量通过选中的提现申请'

    def reject_withdrawals(self, request, queryset):
        queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
    reject_withdrawals.short_description = '批量拒绝选中的提现申请' 