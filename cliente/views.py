from django.shortcuts import render

from cliente.models import Cliente


# Create your views here.
def client_page(request):
    if request.method == 'POST':
        cliente = Cliente()
        cliente.nombre = request.POST['nombre']
        cliente.email = request.POST['email']
        cliente.telefono = request.POST['telefono']
        cliente.mensaje = request.POST['mensaje']
        cliente.save()
    return render(request, 'client/page.html')