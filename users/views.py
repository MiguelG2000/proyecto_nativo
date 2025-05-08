
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from datetime import datetime
from cotizaciones.models import Cotizaciones, CotizacionProduct
from products.models import Product
from cliente.models import Cliente
from users.models import Event
from datetime import timedelta
from django.utils import timezone
from mfa.views import LoginWithOTPView

# Create your views here.
def login(request):
    if not request.user.is_authenticated:
        return LoginWithOTPView.as_view()(request)

    user = request.user
    name = user.first_name
    products_alert = Product.objects.filter(inventario__lte=10)
    cotizaciones = Cotizaciones.objects.filter(status="Pendiente").count()
    productos = Product.objects.filter(otro=False).count()

    today = timezone.now().date()
    seven_days_later = today + timedelta(days=7)

    upcoming_deliveries = Cotizaciones.objects.filter(
        status="Aceptado",
        fecha_entrega__gte=today,
        fecha_entrega__lte=seven_days_later
    ).order_by('fecha_entrega')[:5]

    upcoming_events = Event.objects.filter(
        fecha__gte=today,
        fecha__lte=seven_days_later
    ).order_by('fecha')[:5]

    notificaciones = len(products_alert) + len(upcoming_deliveries) + len(upcoming_events)
    mensajes = Cliente.objects.all()
    mes_actual = datetime.now().month

    total_mes_query = (
        CotizacionProduct.objects
        .filter(
            Q(cotizacion_id__status="Aceptado") | Q(cotizacion_id__status="Completado"),
            cotizacion_id__fecha__month=mes_actual
        )
        .aggregate(total_civa=Sum('cotizacion_id__total_Civa'))
    )

    # Extraer el valor del total con IVA o usar 0 si es None
    total_mes = total_mes_query['total_civa'] or 0.0

    # Guardarlo en la sesión para mantener consistencia con el código existente
    request.session['totalCiva'] = float(total_mes)

    context = {
        'user': user,
        'name': name,
        'products_alert': products_alert,
        'total_mes': float(total_mes),  # Usar el valor calculado directamente
        'cotizaciones': cotizaciones,
        'productos': productos,
        'upcoming_deliveries': upcoming_deliveries,
        'upcoming_events': upcoming_events,
        'notificaciones': notificaciones,
        'mensajes': mensajes,
        'empleado': not user.is_staff,  # Asumiendo que "empleado" indica si no es staff
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

def creators(request):
    return render(request, 'creators.html')