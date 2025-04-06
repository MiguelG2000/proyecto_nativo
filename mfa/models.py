from django.db import models
from django.contrib.auth.models import User
import pyotp

class UserMFA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa')
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)

    def generate_mfa_secret(self):
        self.mfa_secret = pyotp.random_base32()

    def get_totp_uri(self):
        if not self.mfa_secret:
            return None
        return f'otpauth://totp/mfa:{self.user.username}?secret={self.mfa_secret}&issuer=TuApp'
