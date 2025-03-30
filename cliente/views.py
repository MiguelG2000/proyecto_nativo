from lib2to3.fixes.fix_input import context

from django.shortcuts import render

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
