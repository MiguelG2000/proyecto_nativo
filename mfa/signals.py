from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserMFA

@receiver(post_save, sender=User)
def create_user_mfa(sender, instance, created, **kwargs):
    if created:
        UserMFA.objects.create(user=instance)