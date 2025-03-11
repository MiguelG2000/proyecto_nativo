from multiprocessing.reduction import register

from django.contrib import admin
from users.models import Event

# Register your models here.
admin.site.register(Event)