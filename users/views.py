from lib2to3.fixes.fix_input import context

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect


# Create your views here.
def login(request):
    if not request.user.is_authenticated:
        return LoginView.as_view(template_name="login.html")(request)
    user = request.user
    name = request.user.first_name
    context = {
        'user': user,
        'name': name,
    }
    return render (request, "index.html", context)

