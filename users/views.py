
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from cotizaciones.models import Cotizaciones
from products.models import Product
from cliente.models import Cliente
from users.models import Event
from datetime import timedelta
from django.utils import timezone

# Create your views here.


def login(request):
    if not request.user.is_authenticated:
        return LoginView.as_view(template_name="login.html")(request)
    user = request.user
    name = request.user.first_name
    # Obtener productos con bajo inventario
    products_alert = Product.objects.filter(inventario__lte=10)
    # Obtener cotizaciones pendientes
    cotizaciones = Cotizaciones.objects.filter(status="Pendiente").count()
    # Obtener productos activos
    productos = Product.objects.filter(otro=False).count()
    # Obtener próximas fechas de entrega (dentro de los próximos 7 días)
    today = timezone.now().date()  # Fecha actual
    seven_days_later = today + timedelta(days=7)# Fecha dentro de 7 días

    upcoming_deliveries = Cotizaciones.objects.filter(
        status="Aceptado",
        fecha_entrega__gte=today,  # Fechas mayores o iguales a hoy
        fecha_entrega__lte=seven_days_later  # Fechas menores o iguales a 7 días después
    ).order_by('fecha_entrega')[:5]

    # Obtener eventos próximos (dentro de los próximos 7 días)
    upcoming_events = Event.objects.filter(
        fecha__gte=today,
        fecha__lte=seven_days_later
    ).order_by('fecha')[:5]

    notificaciones = len(products_alert) + len(upcoming_deliveries) + len(upcoming_events)

    #Extraer atributos de Cliente
    mensajes = Cliente.objects.all()

    context = {
        'user': user,
        'name': name,
        'products_alert': products_alert,
        'total_mes': request.session.get('totalCiva', 0),
        'cotizaciones': cotizaciones,
        'productos': productos,
        'upcoming_deliveries': upcoming_deliveries,
        'upcoming_events': upcoming_events,
        'notificaciones': notificaciones,
        'mensajes': mensajes,
    }
    return render(request, "index/index.html", context)


def calendar (request):
    fechas = Cotizaciones.objects.filter(status="Aceptado")
    for fecha in fechas:
        fecha.fecha_entrega = fecha.fecha_entrega.strftime("%Y-%m-%d")

    events = Event.objects.all()
    for event in events:
        event.fecha = event.fecha.strftime("%Y-%m-%d")

    context = {
        'fechas': fechas,
        'events': events,
    }
    print(events)
    return render (request, "calendar.html", context)

def add_event(request):
    if request.method == "POST":
        event = Event()
        event.nombre = request.POST["nombre"]
        event.fecha = request.POST["fecha"]
        event.save()
        messages.success(request, "Evento agregado correctamente.")
        return redirect(reverse_lazy('calendar'))
    return render(request, 'calendar.html')

def delete_message(request, cliente_id):
    Cliente.objects.get(cliente_id=cliente_id).delete()
    return redirect(reverse_lazy('login'))
