from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime

from cotizaciones.models import CotizacionProduct

def report_dashboard(request):
    mes_seleccionado = request.GET.get('mes', str(datetime.now().month))
    grafica = (
        CotizacionProduct.objects
        .filter(
            cotizacion_id__status="Aceptado",
            product_id__otro=False,
            cotizacion_id__fecha__month=mes_seleccionado
        )
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

    if grafica:
        totalCiva = float(grafica[0]['totalCiva'])
        totalSiva = float(grafica[0]['totalSiva'])
    else:
        totalCiva = 0.0
        totalSiva = 0.0

    context = {
        'labels': labels,
        'data': data,
        'totalCiva': totalCiva,
        'totalSiva': totalSiva,
        'mes_seleccionado': mes_seleccionado
    }

    return render(request, 'report/report.html', context)
