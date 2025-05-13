from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import Sum
from .models import User, UserProfile, MemberLevel, Commission, CommissionHistory, DistributorProfile, WithdrawalRecord, CommissionRecord, Notification
from dashboard.mixins import ExportableModelAdmin

class DistributorProfileInline(admin.StackedInline):
    model = DistributorProfile
    can_delete = False
    verbose_name_plural = _('分销商资料')
    fk_name = 'user'

@admin.register(MemberLevel)
class MemberLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'points_required', 'discount', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('level',)

@admin.register(User)
class CustomUserAdmin(ExportableModelAdmin, BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'gender', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('user__username', 'nickname')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'source', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'description')

@admin.register(CommissionHistory)
class CommissionHistoryAdmin(admin.ModelAdmin):
    list_display = ('commission', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('commission__user__username', 'remark')

@admin.register(DistributorProfile)
class DistributorProfileAdmin(ExportableModelAdmin):
    list_display = ('user', 'level', 'commission_rate', 'is_approved', 'created_at')
    list_filter = ('level', 'is_approved', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'level', 'commission_rate', 'is_approved', 'created_at')
    ordering = ('-created_at',)

@admin.register(WithdrawalRecord)
class WithdrawalRecordAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'amount', 'status', 'bank_name', 'account_holder', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('distributor__user__username', 'account_holder', 'bank_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('distributor', 'amount', 'status')
        }),
        ('银行信息', {
            'fields': ('bank_name', 'account_holder', 'account_number')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('distributor__user')

@admin.register(CommissionRecord)
class CommissionRecordAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'amount', 'level', 'status', 'created_at')
    list_filter = ('status', 'level', 'created_at')
    search_fields = ('distributor__user__username', 'remark')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'content')
