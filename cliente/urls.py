from django.urls import path
from .views import client_page

urlpatterns = [
    path('', client_page, name="client_page"),
]