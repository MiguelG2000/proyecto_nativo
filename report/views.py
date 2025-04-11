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
            total_vendido=Sum('cantidad')
        )
        .order_by('-total_vendido')[:10]
    )

    # Preparar los datos para la gráfica de productos más vendidos
    labels = [producto['product_id__nombre'] for producto in grafica]
    data = [producto["total_vendido"] for producto in grafica]

    # Calcular totales con y sin IVA de manera separada para todo el mes
    total_query = (
        CotizacionProduct.objects
        .filter(
            Q(cotizacion_id__status="Aceptado") | Q(cotizacion_id__status="Completado"),
            cotizacion_id__fecha__month=mes_seleccionado
        )
        .aggregate(
            totalCiva=Sum('cotizacion_id__total_Civa'),
            totalSiva=Sum('cotizacion_id__total')
        )
    )

    # Extraer los valores o usar 0 si son None
    totalCiva = float(total_query['totalCiva'] or 0.0)
    totalSiva = float(total_query['totalSiva'] or 0.0)

    # Guardar en la sesión para uso en otras vistas
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