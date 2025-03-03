from django.shortcuts import render
from django.db.models import Sum
from cotizaciones.models import Cotizaciones, CotizacionProduct
from products.models import Product

# Create your views here.
def report_dashboard(request):
    grafica = ( CotizacionProduct.objects
                .filter(cotizacion_id__status="Aceptado")
                .values('product_id__nombre')
                .annotate(total_vendido=Sum('cantidad'))
                .order_by('-total_vendido')[:10]
                )

    labels = [producto['product_id__nombre'] for producto in grafica]
    data = [producto["total_vendido"] for producto in grafica]

    context = {
        'labels': labels,
        'data': data
    }

    print(str(grafica))
    return render(request, 'report/dashboard.html', context)