from django.db.models import Sum, Q
from datetime import datetime

from django.shortcuts import render

from cotizaciones.models import CotizacionProduct

def report_dashboard(request):
    mes_seleccionado = request.GET.get('mes', str(datetime.now().month))

    # Consulta para obtener los productos más vendidos
    grafica = (
        CotizacionProduct.objects
        .filter(
            Q(cotizacion_id__status="Aceptado") | Q(cotizacion_id__status="Completado"),
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

    # Preparar los datos para la gráfica de productos más vendidos
    labels = [producto['product_id__nombre'] for producto in grafica]
    data = [producto["total_vendido"] for producto in grafica]

    # Calcular totales con y sin IVA
    if grafica:
        totalCiva = float(grafica[0]['totalCiva'])
        totalSiva = float(grafica[0]['totalSiva'])
    else:
        totalCiva = 0.0
        totalSiva = 0.0

    request.session['totalCiva'] = totalCiva

    # Pasar los datos al contexto
    context = {
        'labels': labels,
        'data': data,
        'totalCiva': totalCiva,
        'totalSiva': totalSiva,
        'mes_seleccionado': mes_seleccionado
    }

    return render(request, 'report/report.html', context)