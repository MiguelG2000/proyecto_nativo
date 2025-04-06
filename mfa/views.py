from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.contrib import messages
import pyotp

class LoginWithOTPView(DjangoLoginView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        token = request.POST.get("token")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            mfa = getattr(user, "mfa", None)
            if mfa and mfa.mfa_enabled:
                if not token:
                    messages.error(request, "Se requiere el código OTP.")
                    return render(request, self.template_name)
                totp = pyotp.TOTP(mfa.mfa_secret)
                if not totp.verify(token):
                    messages.error(request, "Código OTP inválido.")
                    return render(request, self.template_name)

        return super().post(request, *args, **kwargs)
