from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from .utils import ExportMixin

class ExportableModelAdmin(admin.ModelAdmin, ExportMixin):
    """
    支持导出的ModelAdmin基类
    """
    change_list_template = 'admin/exportable_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/<str:format>/', self.export_view, name='export'),
        ]
        return custom_urls + urls

    def export_view(self, request, format):
        """处理导出请求"""
        queryset = self.get_queryset(request)
        
        if format == 'xlsx':
            filepath = self.export_excel(queryset, request)
        elif format == 'csv':
            filepath = self.export_csv(queryset, request)
        elif format == 'pdf':
            filepath = self.export_pdf(queryset, request)
        else:
            return HttpResponse('不支持的导出格式')

        return self.get_export_response(filepath, format)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['export_formats'] = [
            ('xlsx', 'Excel'),
            ('csv', 'CSV'),
            ('pdf', 'PDF'),
        ]
        return super().changelist_view(request, extra_context=extra_context) 