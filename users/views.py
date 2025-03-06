from lib2to3.fixes.fix_input import context

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from datetime import datetime
from cotizaciones.models import Cotizaciones
from products.models import Product


# Create your views here.

def login(request):
    if not request.user.is_authenticated:
        return LoginView.as_view(template_name="login.html")(request)
    user = request.user
    name = request.user.first_name

    products_alert = Product.objects.filter(inventario__lte = 10)
    total_mes = request.session.get('totalCiva', 0)
    cotizaciones = Cotizaciones.objects.filter(status = "Pendiente").count()
    productos = Product.objects.filter(otro = False).count()

    context = {
        'user': user,
        'name': name,
        'products_alert': products_alert,
        'total_mes': total_mes,
        'cotizaciones': cotizaciones,
        'productos': productos,
    }
    return render (request, "index.html", context)
