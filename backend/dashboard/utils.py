import os
import csv
import xlsxwriter
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import ExportRecord

class ExportMixin:
    """
    导出功能混入类
    """
    def get_export_filename(self, format_type):
        """生成导出文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{self.model.__name__}_{timestamp}.{format_type}"

    def get_export_fields(self):
        """获取要导出的字段"""
        return [field.name for field in self.model._meta.fields]

    def get_export_headers(self):
        """获取导出表头"""
        return [field.verbose_name for field in self.model._meta.fields]

    def export_excel(self, queryset, request):
        """导出Excel"""
        filename = self.get_export_filename('xlsx')
        filepath = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet()

        # 写入表头
        headers = self.get_export_headers()
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # 写入数据
        fields = self.get_export_fields()
        for row, obj in enumerate(queryset, start=1):
            for col, field in enumerate(fields):
                value = getattr(obj, field)
                worksheet.write(row, col, str(value))

        workbook.close()

        # 记录导出记录
        ExportRecord.objects.create(
            user=request.user,
            model_name=self.model.__name__,
            format='xlsx',
            file_path=filepath,
            file_size=os.path.getsize(filepath)
        )

        return filepath

    def export_csv(self, queryset, request):
        """导出CSV"""
        filename = self.get_export_filename('csv')
        filepath = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(self.get_export_headers())
            
            fields = self.get_export_fields()
            for obj in queryset:
                row = [str(getattr(obj, field)) for field in fields]
                writer.writerow(row)

        # 记录导出记录
        ExportRecord.objects.create(
            user=request.user,
            model_name=self.model.__name__,
            format='csv',
            file_path=filepath,
            file_size=os.path.getsize(filepath)
        )

        return filepath

    def export_pdf(self, queryset, request):
        """导出PDF"""
        filename = self.get_export_filename('pdf')
        filepath = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []

        # 准备数据
        data = [self.get_export_headers()]
        fields = self.get_export_fields()
        for obj in queryset:
            row = [str(getattr(obj, field)) for field in fields]
            data.append(row)

        # 创建表格
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)

        # 记录导出记录
        ExportRecord.objects.create(
            user=request.user,
            model_name=self.model.__name__,
            format='pdf',
            file_path=filepath,
            file_size=os.path.getsize(filepath)
        )

        return filepath

    def get_export_response(self, filepath, format_type):
        """生成下载响应"""
        with open(filepath, 'rb') as f:
            response = HttpResponse(f.read(), content_type=f'application/{format_type}')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            return response 