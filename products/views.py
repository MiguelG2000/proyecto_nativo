from lib2to3.fixes.fix_input import context

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from products.models import Product


# Create your views here.
def hello(request):
    return HttpResponse("Hola productos")

#CRUD
def products_view(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, 'inventario.html', context)


def create_product(request):
    if request.method == 'POST':
        product = Product()
        product.nombre = request.POST['nombre']
        product.descripcion = request.POST['descripcion']
        product.categoria = request.POST['categoria']
        product.volumen = request.POST['volumen']
        product.unidad = request.POST['unidad']
        product.inventario = request.POST['inventario']
        product.precio_general = request.POST['precio_general']
        product.precio_distribuidor = request.POST['precio_distribuidor']
        product.save()
        return redirect(reverse_lazy('products'))
    return render(request, 'form.html')

def update_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == "POST":
        product.nombre = request.POST['nombre']
        product.descripcion = request.POST['descripcion']
        product.categoria = request.POST['categoria']
        product.volumen = request.POST['volumen']
        product.unidad = request.POST['unidad']
        product.inventario = request.POST['inventario']
        product.precio_general = request.POST['precio_general']
        product.precio_distribuidor = request.POST['precio_distribuidor']
        product.save()
        return redirect(reverse_lazy('products'))
    context = {"product": product}
    return render(request, 'form.html', context)

def delete_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    return redirect(reverse_lazy('products'))
