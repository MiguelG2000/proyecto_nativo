from lib2to3.fixes.fix_input import context

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from cliente.models import Cliente


# Create your views here.
def client_page(request):
    if request.method == 'POST':
        cliente = Cliente()
        cliente.nombre = request.POST['nombre']
        cliente.telefono = request.POST['telefono']
        cliente.mensaje = request.POST['mensaje']
        cliente.save()
    return render(request, 'client/page.html')

def view_client(request):
    clientes = Cliente.objects.all()
    context = {
        'clientes': clientes
    }
    return render(request, 'quotes/clients.html', context)

def create_client(request):
    if request.method == 'POST':
        cliente = Cliente()
        cliente.nombre = request.POST['nombre']
        cliente.telefono = request.POST['telefono']
        cliente.save()
        return redirect(reverse_lazy(view_client))


def edit_client(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        cliente.nombre = request.POST['nombre']
        cliente.telefono = request.POST['telefono']
        cliente.save()
        return redirect(reverse_lazy('view_client'))


    clientes = Cliente.objects.all()
    context = {
        'cliente': cliente,
        'clientes': clientes
    }
    return render(request, 'quotes/clients.html', context)

def delete_client(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    cliente.delete()
    return redirect(reverse_lazy(view_client))
