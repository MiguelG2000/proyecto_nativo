# admin.py

from django.contrib import admin
from .models import UserMFA
import pyotp
import qrcode
import io
import base64
from django.utils.html import format_html

@admin.register(UserMFA)
class UserMFAAdmin(admin.ModelAdmin):
    list_display = ("user", "mfa_enabled")
    readonly_fields = ("qr_code",)

    def save_model(self, request, obj, form, change):
        if obj.mfa_enabled and not obj.mfa_secret:
            obj.generate_mfa_secret()
        super().save_model(request, obj, form, change)

    def qr_code(self, obj):
        if not obj.mfa_secret:
            return "Guarde para generar el código."
        uri = obj.get_totp_uri()
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        return format_html(f'<img src="data:image/png;base64,{img_b64}" width="200"/>')

    qr_code.short_description = "Código QR MFA"
