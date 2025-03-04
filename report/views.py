from django.shortcuts import render
from django.db.models import Sum
from cotizaciones.models import Cotizaciones, CotizacionProduct
from products.models import Product

# Create your views here.
def report_dashboard(request):
    grafica = ( CotizacionProduct.objects
                .filter(cotizacion_id__status="Aceptado", product_id__otro=False)
                .values('product_id__nombre')
                .annotate(
                            total_vendido=Sum('cantidad'),
                            totalCiva=Sum('cotizacion_id__total_Civa'),
                            totalSiva=Sum('cotizacion_id__total')
                )
                .order_by('-total_vendido')[:10]
                )

    labels = [producto['product_id__nombre'] for producto in grafica]
    data = [producto["total_vendido"] for producto in grafica]
    totalCiva = float(grafica[0]['totalCiva'])
    totalSiva = float(grafica[0]['totalSiva'])

    context = {
        'labels': labels,
        'data': data,
        'totalCiva': totalCiva,
        'totalSiva': totalSiva
    }

    return render(request, 'report/dashboard.html', context)