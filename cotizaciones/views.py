from itertools import product
from lib2to3.fixes.fix_input import context

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse

from cotizaciones.models import Cotizaciones, CotizacionProduct
from products.models import Product
from cliente.models import Cliente

# Create your views here.
def quotes_view(request):
    cotizaciones = Cotizaciones.objects.all()
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

    context = {
        'cotizaciones': cotizacion,
        'cotProduct': productNormal,
        'productOtro': productPersonalizado,
        'products': products,
    }
    return render(request, 'quotes/details.html', context)


def create_quote(request):
    if request.method == 'POST':
        quote = Cotizaciones()
        quote.fecha = request.POST['fecha']
        quote.fecha_propuesta = request.POST['fecha_propuesta']
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.metodo_pago = request.POST['metodo_pago']
        quote.servicio_envio = request.POST['servicio_envio']
        quote.costo_envio = request.POST['costo_envio']
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
        quote.id = request.POST['id']
        quote.fecha = request.POST['fecha']
        quote.fecha_propuesta = request.POST['fecha_propuesta']
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.metodo_pago = request.POST['metodo_pago']
        quote.servicio_envio = request.POST['servicio_envio']
        quote.costo_envio = request.POST['costo_envio']

        # Capturar si se aplica IVA 8% o 16%
        quote.iva_8 = 'iva_8' in request.POST
        quote.iva_16 = 'iva_16' in request.POST

        # Verificar si cambió el estado a "Aceptado"
        if prev_status != "Aceptado" and quote.status == "Aceptado":
            for item in quote.cotizaciones.all():
                if item.product_id.inventario is not None:
                    item.product_id.inventario -= item.cantidad
                    item.product_id.save()

        # Guardar los cambios
        quote.save()

        # Calcular el total con IVA
        quote.calcular_iva()

        return redirect(reverse_lazy('details', kwargs={'id': quote.id}))

    context = {"quote": quote}
    return render(request, 'quotes/form.html', context)


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
