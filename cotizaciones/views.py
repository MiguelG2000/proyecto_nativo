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
    cotizaciones = Cotizaciones.objects.get(id=id)
    cotProduct = CotizacionProduct.objects.filter(cotizacion_id=id)
    products = Product.objects.filter(otro = False)
    context = {'cotizaciones': cotizaciones, 'cotProduct': cotProduct, 'products': products}
    return render(request, 'quotes/details.html',context)

def create_quote(request):
    if request.method == 'POST':
        quote = Cotizaciones()
        quote.fecha = request.POST['fecha']
        quote.fecha_propuesta = request.POST['fecha_propuesta']
        quote.total = request.POST['total']
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.restante = request.POST['restante']
        quote.metodo_pago = request.POST['metodo_pago']
        quote.save()
        return redirect(reverse_lazy('list_quotes'))
    return render(request, 'quotes/form.html')


def update_quote(request, id):
    quote = Cotizaciones.objects.get(id=id)
    if request.method == "POST":
        quote.id = request.POST['id']
        quote.fecha = request.POST['fecha']
        quote.fecha_propuesta = request.POST['fecha_propuesta']
        quote.total = request.POST['total']
        quote.status = request.POST['status']
        quote.anticipo = request.POST['anticipo']
        quote.restante = request.POST['restante']
        quote.metodo_pago = request.POST['metodo_pago']
        quote.save()
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

        messages.success(request, "Producto agregado correctamente.")
        return redirect('details', id=cotizacion.id)



def delete_product_from_quote(request, id):
    cotizacion_product = get_object_or_404(CotizacionProduct, id=id)
    cotizacion_id = cotizacion_product.cotizacion_id.id
    cotizacion_product.delete()
    cotizacion_product.cotizacion_id.update_total()

    return redirect(reverse('details', kwargs={'id': cotizacion_id}))
