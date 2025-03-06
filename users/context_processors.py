from django.contrib.auth.models import Group

def empleado_context(request):
    if request.user.is_authenticated:
        empleado = request.user.groups.filter(name='Empleado').exists()
    else:
        empleado = False  # Si no está autenticado, no es parte del grupo
    return {'empleado': empleado}