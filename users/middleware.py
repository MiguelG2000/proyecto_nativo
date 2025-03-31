from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = ['/', '/logout/', '/admin/', '/employee/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in EXEMPT_URLS:
            return redirect(settings.LOGIN_URL or "/employee/")  # Redirigir al login
        return self.get_response(request)