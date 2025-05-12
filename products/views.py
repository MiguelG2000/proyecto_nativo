from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.contrib import messages
from .forms import ProductForm
from products.models import Product, Categorias, Unidades

# Create your views here.
#CRUD
def products_view(request):
    products = Product.objects.filter(otro = False)
    context = {"products": products}
    return render(request, 'products/inventario.html', context)


def create_product(request):
    categorias = Categorias.objects.all()
    unidades = Unidades.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect(reverse_lazy('products'))
        else:
            # Si el formulario no es válido, agregar errores al contexto
            errors = form.errors.as_data()
            error_messages = []
            for field, error_list in errors.items():
                for error in error_list:
                    error_messages.append(f"{field}: {error.message}")
            messages.error(request, "\n".join(error_messages))
    else:
        form = ProductForm()

    context = {
        "form": form,
        "categorias": categorias,
        "unidades": unidades
    }
    return render(request, 'products/form.html', context)

def update_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categorias = Categorias.objects.all()
    unidades = Unidades.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect(reverse_lazy('products'))
        else:
            # Si el formulario no es válido, agregar errores al contexto
            errors = form.errors.as_data()
            error_messages = []
            for field, error_list in errors.items():
                for error in error_list:
                    error_messages.append(f"{field}: {error.message}")
            messages.error(request, "\n".join(error_messages))
    else:
        form = ProductForm(instance=product)

    context = {
        "product": product,
        "form": form,
        "categorias": categorias,
        "unidades": unidades,
    }
    return render(request, 'products/form.html', context)

def delete_product(request, product_id):
    Product.objects.get(id=product_id).delete()
    return redirect(reverse_lazy('products'))

def category_unit(request):
    categorias = Categorias.objects.all()
    unidades = Unidades.objects.all()
    context ={
        'categorias': categorias,
        'unidades': unidades,
    }
    return render(request, 'products/categorias.html', context)

def create_category(request):
    if request.method == 'POST':
        categoria = Categorias()
        categoria.nombre = request.POST['nombre']
        categoria.save()
        return redirect(reverse_lazy('category_unit'))

def delete_category(request, category_id):
    Categorias.objects.get(id=category_id).delete()
    return redirect(reverse_lazy('category_unit'))

def create_unit(request):
    if request.method == 'POST':
        unidad = Unidades()
        unidad.nombre = request.POST['nombre']
        unidad.save()
        return redirect(reverse_lazy('category_unit'))

def delete_unit(request, unit_id):
    Unidades.objects.get(id=unit_id).delete()
    return redirect(reverse_lazy('category_unit'))