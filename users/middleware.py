from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = ['/', '/logout/', '/employee/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Si es una URL exenta o pertenece al admin
        if (
                request.user.is_authenticated or
                path in EXEMPT_URLS or
                path.startswith('/admin/')
        ):
            return self.get_response(request)

        return redirect(settings.LOGIN_URL or "/employee/")