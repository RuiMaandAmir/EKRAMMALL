from django.utils.deprecation import MiddlewareMixin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from .models import AdminLog

class AdminLogMiddleware(MiddlewareMixin):
    """
    管理员操作日志中间件
    """
    def process_response(self, request, response):
        # 只记录管理员操作
        if not request.user.is_authenticated or not request.user.is_staff:
            return response

        # 只记录POST请求
        if request.method != 'POST':
            return response

        # 获取操作类型
        action = None
        if '_save' in request.POST:
            action = CHANGE
        elif '_add' in request.POST:
            action = ADDITION
        elif '_delete' in request.POST:
            action = DELETION

        if not action:
            return response

        # 获取操作对象
        content_type_id = request.POST.get('content_type_id')
        object_id = request.POST.get('object_id')
        
        if not content_type_id or not object_id:
            return response

        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model = content_type.model_class()
            obj = model.objects.get(id=object_id)
            
            # 记录操作日志
            AdminLog.objects.create(
                user=request.user,
                action=action,
                content_type=content_type,
                object_id=object_id,
                change_message=f'修改了 {obj}',
                ip_address=self.get_client_ip(request)
            )
        except Exception:
            pass

        return response

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 