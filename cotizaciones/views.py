from lib2to3.fixes.fix_input import context
from xml.sax.handler import property_interning_dict

import qrcode
from io import BytesIO
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from babel.dates import format_date
from django.utils.dateparse import parse_date
from django.utils.timezone import now, timedelta
from collections import defaultdict
from django.db.models import Sum

from products.models import Product

from cotizaciones.models import (
    Cotizaciones,
    CotizacionProduct,
    Remisiones,
    Entregas
    )

# Create your views here.
def quotes_view(request):
    cotizaciones = Cotizaciones.objects.all()

    for cotizacion in cotizaciones:
        cotizacion.fecha = format_date(cotizacion.fecha, format="full", locale="es")
        cotizacion.fecha_propuesta = format_date(cotizacion.fecha_propuesta, format="full", locale="es")
        cotizacion.fecha_entrega = format_date(cotizacion.fecha_entrega, format="full", locale="es")

    context = {'cotizaciones': cotizaciones}
    return render(request, 'quotes/cotizaciones.html', context)

def details_view(request, id):
    cotizacion = get_object_or_404(Cotizaciones, id=id)
    # Filtrar los productos de la cotización:
    cotProduct = CotizacionProduct.objects.filter(cotizacion_id=cotizacion)
    # Filtrar los productos normales (listados previamente en la base de datos)
    productNormal = cotProduct.filter(product_id__otro=False)
    # Filtrar los productos personalizados (creados manualmente en la cotización)
    productPersonalizado = cotProduct.filter(product_id__otro=True)
    # Filtrar productos disponibles para agregar
    products = Product.objects.filter(otro=False)

    def formatear_fecha(fecha):
        if fecha:  # Verifica que la fecha no sea None
            if isinstance(fecha, datetime):
                return format_date(fecha, format="EEEE d 'de' MMMM 'del' y", locale='es')
            else:
                return format_date(datetime(fecha.year, fecha.month, fecha.day), format="EEEE d 'de' MMMM 'del' y",
                                   locale='es')
        return None

    def formato_moneda(valor):
        return "{:,.2f}".format(valor)

    cotizacion.fecha = formatear_fecha(cotizacion.fecha)
    cotizacion.fecha_propuesta = formatear_fecha(cotizacion.fecha_propuesta)
    cotizacion.fecha_entrega = formatear_fecha(cotizacion.fecha_entrega)

    # Formatear los valores de la cotización
    cotizacion.costo_envio = formato_moneda(cotizacion.costo_envio)
    cotizacion.total = formato_moneda(cotizacion.total)
    cotizacion.total_Civa = formato_moneda(cotizacion.total_Civa)
    cotizacion.anticipo = formato_moneda(cotizacion.anticipo)
    cotizacion.restante = formato_moneda(cotizacion.restante)
    cotizacion.iva = formato_moneda(cotizacion.iva)

    qr_image = generate_qr(cotizacion.direccion_entrega)

    context = {
        'cotizaciones': cotizacion,
        'cotProduct': productNormal,
        'productOtro': productPersonalizado,
        'products': products,
        'qr_image': qr_image,

    }
    return render(request, 'quotes/details.html', context)


def generate_qr(direccion):
    # Crear el código QR con la dirección de entrega
    qr = qrcode.make(direccion)

    # Guardar el código QR en un objeto BytesIO para poder ser enviado en la respuesta
    qr_image = BytesIO()
    qr.save(qr_image, format='PNG')
    qr_image.seek(0)

    return qr_image


def create_quote(request):
    if request.method == 'POST':
        fecha_entrega = request.POST.get("fecha_entrega", "").strip()
        fecha_entrega = parse_date(fecha_entrega) if fecha_entrega else None

        quote = Cotizaciones()
        quote.fecha = request.POST.get('fecha')
        quote.fecha_propuesta = request.POST.get('fecha_propuesta') or (now().date() + timedelta(days=7))
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.metodo_pago = request.POST['metodo_pago']
        quote.servicio_envio = request.POST['servicio_envio']
        quote.costo_envio = request.POST['costo_envio']
        quote.cliente = request.POST['cliente']
        quote.telefono = request.POST['telefono']
        quote.fecha_entrega = fecha_entrega
        quote.direccion_entrega = request.POST['direccion_entrega']

        # Capturar si se aplica IVA 8% o 16%
        quote.iva_8 = 'iva_8' in request.POST
        quote.iva_16 = 'iva_16' in request.POST

        quote.save()
        quote.calcular_iva()

        return redirect(reverse_lazy('list_quotes'))
    return render(request, 'quotes/form.html')


def update_quote(request, id):
    quote = get_object_or_404(Cotizaciones, id=id)

    if request.method == "POST":
        prev_status = quote.status  # Guardar el estado anterior

        # Actualizar los campos con los datos del formulario
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.metodo_pago = request.POST['metodo_pago']
        fecha_entrega = request.POST.get('fecha_entrega', '').strip()
        quote.fecha_entrega = fecha_entrega if fecha_entrega else None
        quote.direccion_entrega = request.POST['direccion_entrega']

        # Verificar si cambió el estado a "Aceptado"
        if prev_status != "Aceptado" and quote.status == "Aceptado":
            for item in quote.cotizaciones.all():
                if item.product_id.inventario is not None:
                    item.product_id.inventario -= item.cantidad
                    item.product_id.save()

        quote.save()
        quote.calcular_iva()

        return redirect(reverse_lazy('details', kwargs={'id': quote.id}))

    context = {"quote": quote}
    return render(request, 'quotes/formUpdate.html', context)


def delete_quote(request, id):
    Cotizaciones.objects.get(id=id).delete()
    return redirect(reverse_lazy('list_quotes'))

#------------------------------------------------------------------------------------

def add_product_to_quote(request, id):
    if request.method == "POST":
        cotizacion = get_object_or_404(Cotizaciones, id=id)
        product = get_object_or_404(Product, id=request.POST["producto"])
        cantidad_nueva = int(request.POST["cantidad"])
        usar_precio_distribuidor = request.POST.get("usar_precio_distribuidor") == "on"

        # Buscar si el producto ya está en la cotización con el mismo tipo de precio
        cotizacion_producto, created = CotizacionProduct.objects.get_or_create(
            cotizacion_id=cotizacion,
            product_id=product,
            usar_precio_distribuidor=usar_precio_distribuidor,
            defaults={'cantidad': cantidad_nueva}
        )

        if not created:
            # Si ya existía, solo aumentar la cantidad
            cotizacion_producto.cantidad += cantidad_nueva
            cotizacion_producto.save()

        # Actualizar total de la cotización
        cotizacion.update_total()
        cotizacion.calcular_iva()

        messages.success(request, "Producto agregado correctamente.")
        return redirect('details', id=cotizacion.id)


def add_custom_product_to_quote(request, id):
    if request.method == "POST":
        cotizacion = get_object_or_404(Cotizaciones, id=id)

        # Convertir los valores a tipos numéricos correctos
        largo = float(request.POST["largo"]) if request.POST["largo"] else 0
        ancho = float(request.POST["ancho"]) if request.POST["ancho"] else 0
        alto = float(request.POST["alto"]) if request.POST["alto"] else 0
        precio_general = float(request.POST["precio_general"]) if request.POST["precio_general"] else 0
        cantidad = int(request.POST["cantidad"]) if request.POST["cantidad"] else 1  # Asegurar un valor por defecto

        # Crear un producto personalizado
        product = Product.objects.create(
            nombre=request.POST["nombre"],
            largo=largo,
            ancho=ancho,
            alto=alto,
            precio_general=precio_general,
            otro=True  # Marcamos como personalizado
        )

        # Asociar el producto a la cotización
        CotizacionProduct.objects.create(
            cotizacion_id=cotizacion,
            product_id=product,
            cantidad=cantidad,
            phistorico=product.precio_general,
            usar_precio_distribuidor=False
        )

        product.update_volumen()
        cotizacion.calcular_iva()
        messages.success(request, "Producto personalizado agregado con éxito.")
        return redirect(reverse("details", kwargs={"id": id}))

    return redirect(reverse("details", kwargs={"id": id}))

def delete_product_from_quote(request, id):
    cotizacion_product = get_object_or_404(CotizacionProduct, id=id)
    cotizacion_id = cotizacion_product.cotizacion_id.id
    cotizacion_product.delete()
    cotizacion_product.cotizacion_id.update_total()
    cotizacion_product.cotizacion_id.calcular_iva()

    return redirect(reverse('details', kwargs={'id': cotizacion_id}))

#------------------------------------------------------------------------------------
from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Cotizaciones, CotizacionProduct, Remisiones, Entregas

def view_remission(request, id):
    cotizacion = get_object_or_404(Cotizaciones, id=id)
    productos_cotizacion = CotizacionProduct.objects.filter(cotizacion_id=cotizacion)
    remisiones = Remisiones.objects.filter(cotizacion_id=cotizacion)

    if request.method == "POST":
        productos_ids = request.POST.getlist("product_id")
        cantidades_entregadas = request.POST.getlist("cantidad_entregada")

        # Validar antes de procesar
        errores = []
        for producto_id, cantidad_entregada in zip(productos_ids, cantidades_entregadas):
            cantidad_entregada = int(cantidad_entregada)

            # Obtener el producto de la cotización
            cotizacion_producto = CotizacionProduct.objects.filter(
                cotizacion_id=cotizacion,
                product_id=producto_id
            ).first()

            if not cotizacion_producto:
                errores.append(f"El producto con ID {producto_id} no está en la cotización.")
                continue

            # Obtener la remisión existente o crear una nueva
            remision, created = Remisiones.objects.get_or_create(
                cotizacion_id=cotizacion,
                product_id_id=producto_id,
                defaults={"total": 0, "restante": cotizacion_producto.cantidad, "status": "Pendiente"}
            )

            # Validar que no se exceda la cantidad cotizada
            total_entregado = remision.entregas.aggregate(total_entregado=Sum('cantidad_entregada'))['total_entregado'] or 0
            if total_entregado + cantidad_entregada > cotizacion_producto.cantidad:
                errores.append(f"La cantidad entregada excede la cantidad cotizada para el producto {cotizacion_producto.product_id.nombre}.")
                continue

            # Si no hay errores, crear la entrega
            Entregas.objects.create(remision=remision, cantidad_entregada=cantidad_entregada)
            remision.actualizar_totales()

        # Si hay errores, mostrar mensajes y no guardar nada
        if errores:
            return render(request, "quotes/remisiones.html", {
                "cotizacion": cotizacion,
                "productos_cotizacion": productos_cotizacion,
                "remisiones_dict": defaultdict(list),
                "error": errores
            })

        return redirect("view_remission", id=id)

    # Crear un diccionario para agrupar remisiones por producto
    remisiones_dict = {}
    for producto in productos_cotizacion:
        remision = remisiones.filter(product_id=producto.product_id).first()
        remisiones_dict[producto.product_id.id] = {
            "entregas": Entregas.objects.filter(remision__product_id=producto.product_id, remision__cotizacion_id=cotizacion).order_by("id"),
            "remision": remision  # Incluir la instancia de Remisiones
        }

    context = {
        "cotizacion": cotizacion,
        "productos_cotizacion": productos_cotizacion,
        "remisiones_dict": remisiones_dict,
    }

    return render(request, "quotes/remisiones.html", context)
