class AdminLoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.shortcuts import resolve_url
            from django.conf import settings
            
            return redirect_to_login(
                request.get_full_path(),
                resolve_url(settings.LOGIN_URL),
                'next'
            )
        return self.get_response(request)
