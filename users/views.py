from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect


# Create your views here.
def login(request):
    if not request.user.is_authenticated:
        return LoginView.as_view(template_name="login.html")(request)
    return render (request, "index.html")

