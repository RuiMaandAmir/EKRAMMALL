from django.conf import settings

def admin_site_settings(request):
    """
    添加管理站点设置到模板上下文
    """
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'ADMIN_SITE_HEADER': settings.ADMIN_SITE_HEADER,
        'ADMIN_SITE_TITLE': settings.ADMIN_SITE_TITLE,
        'ADMIN_INDEX_TITLE': settings.ADMIN_INDEX_TITLE,
    }

def global_settings(request):
    """
    添加全局设置到模板上下文
    """
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
    } 