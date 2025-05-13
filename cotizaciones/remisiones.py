from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from cotizaciones.models import Cotizaciones, Remisiones, Entregas, CotizacionProduct
from datetime import datetime
from cotizaciones.views import generate_qr

# Diccionario de traducción de días y meses en español
dias_semana = {
    "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
    "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
}

meses = {
    "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
    "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
    "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"
}

def formatear_fecha(fecha):
    fecha_dt = datetime.strptime(str(fecha), "%Y-%m-%d")
    dia_semana = dias_semana[fecha_dt.strftime("%A")]
    dia = fecha_dt.strftime("%d")
    mes = meses[fecha_dt.strftime("%B")]
    anio = fecha_dt.strftime("%Y")
    return f"{dia_semana}, {dia} de {mes} del {anio}"

def verificar_pagina(pdf, y, margen=100):
    """Verifica si hay espacio suficiente en la página para continuar dibujando elementos."""
    if y < margen:
        pdf.showPage()
        agregar_encabezado(pdf)
        return letter[1] - 160
    return y

def agregar_encabezado(pdf):
    """Dibuja el encabezado en cada nueva página."""
    logo_path = "static/img/logo.png"
    pdf.drawImage(ImageReader(logo_path), 40, letter[1] - 120, width=200, height=100, preserveAspectRatio=True, mask='auto')

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(260, letter[1] - 50, "                        GRUPO NATIVO")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(260, letter[1] - 65, "20 Poniente Sur #550B CP. 29070 | Tuxtla Gutiérrez, Chiapas.")
    pdf.drawString(260, letter[1] - 80, "                nativo.tu.mx@gmail.com | 961 693 66 44")

def generate_remission_pdf(request, id):
    """Genera un PDF de Nota de Remisión basado en la cotización."""
    cotizacion = Cotizaciones.objects.get(id=id)
    remisiones = Remisiones.objects.filter(cotizacion_id=cotizacion)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="remision_{cotizacion.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    agregar_encabezado(pdf)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(230, height - 140, "NOTA DE REMISIÓN")

    y = height - 240

    # Datos del Cliente
    y = verificar_pagina(pdf, y)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(40, height - 130, "Datos del cliente:")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, height - 145, f"Cliente: {cotizacion.cliente}")
    pdf.drawString(40, height - 160, f"Teléfono: {cotizacion.telefono}")
    pdf.drawString(40, height - 175, f"Dirección: {cotizacion.direccion_entrega}")

    # Datos de la remisión a la derecha
    margen_derecho = width - 40
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(margen_derecho, height - 130, f"REMISIÓN: {cotizacion.id}")
    pdf.setFont("Helvetica", 8)
    # Obtener la fecha actual formateada
    fecha_dt = datetime.now()
    mes_es = meses[fecha_dt.strftime("%B")]
    fecha_actual = f"{fecha_dt.strftime('%d')} de {mes_es} de {fecha_dt.strftime('%Y')}"
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(margen_derecho, height - 145, f"Fecha: {fecha_actual}")

    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, height - 200,
                   "Estimado cliente, por medio del presente, le hago entrega de la cotización solicitada. Puede corroborar a detalle la presente cotización. ")
    pdf.drawString(40, height - 210,
                   "Cualquier duda favor de contactarnos.")
    # Encabezado de tabla
    y += 10
    pdf.setFont("Helvetica-Bold", 7)
    col_positions = [30, 150, 180, 210, 240, 270, 300, 370, 440, 500, 580]
    headers = ["Concepto", "Cantidad", "Largo", "Ancho", "Alto", "Volumen", "Últimas Entregas", "Total Entregado", "Restante", "Estado"]

    for i in range(len(headers)):
        pdf.drawCentredString((col_positions[i] + col_positions[i + 1]) / 2, y, headers[i])

    pdf.line(30, y + 8, width - 40, y + 8)
    pdf.line(30, y - 5, width - 40, y - 5)
    y -= 20

    pdf.setFont("Helvetica", 8)
    for remision in remisiones:
        y = verificar_pagina(pdf, y + 5, margen=150)

        entregas = Entregas.objects.filter(remision=remision).order_by('-id')
        entregas_lista = [f"{i + 1}er entrega: {ent.cantidad_entregada}" for i, ent in enumerate(entregas)]

        cotizacion_producto = CotizacionProduct.objects.filter(
            cotizacion_id=cotizacion, product_id=remision.product_id
        ).first()
        cantidad_cotizada = cotizacion_producto.cantidad if cotizacion_producto else 0

        # Coordenadas X centrales de las columnas
        x_centros = [(col_positions[i] + col_positions[i + 1]) / 2 for i in range(len(col_positions) - 1)]

        # Obtener producto y decidir qué texto mostrar
        producto = remision.product_id
        nombre_o_descripcion = producto.descripcion if not producto.otro else producto.nombre

        # Calcular el ancho permitido para la columna
        ancho_columna = col_positions[1] - col_positions[0] - 4  # Margen de 2px a cada lado

        # Calcular caracteres aproximados por línea
        caracteres_por_linea = int(ancho_columna / pdf.stringWidth("X", "Helvetica", 8))

        # Dividir en líneas usando wrap
        lineas_concepto = wrap(nombre_o_descripcion, width=caracteres_por_linea)
        num_lineas_concepto = len(lineas_concepto)

        # Medir el número de líneas para entregas
        num_lineas_entregas = max(len(entregas_lista), 1)

        # Calcular altura de la fila tomando el mayor número de líneas
        altura_fila = 15 + 8 * max(num_lineas_entregas, num_lineas_concepto)

        # Imprimir Concepto (alineado a la izquierda con margen)
        pdf.setFont("Helvetica", 8)
        text = pdf.beginText(col_positions[0] + 2, y)
        text.setFont("Helvetica", 8)
        for linea in lineas_concepto:
            text.textLine(linea)
        pdf.drawText(text)

        # Imprimir el resto de columnas alineadas centradas
        pdf.drawCentredString(x_centros[1], y, str(cantidad_cotizada))
        pdf.drawCentredString(x_centros[2], y, f"{remision.product_id.largo or 0.00:.2f}")
        pdf.drawCentredString(x_centros[3], y, f"{remision.product_id.ancho or 0.00:.2f}")
        pdf.drawCentredString(x_centros[4], y, f"{remision.product_id.alto or 0.00:.2f}")
        pdf.drawCentredString(x_centros[5], y, f"{remision.product_id.volumen or 0.00:.2f}")

        # Imprimir entregas multilínea
        text_entregas = pdf.beginText(col_positions[6] + 5, y)
        text_entregas.setFont("Helvetica", 8)
        for entrega in entregas_lista:
            text_entregas.textLine(entrega)
        pdf.drawText(text_entregas)

        # Campos finales
        pdf.drawCentredString(x_centros[7], y, str(remision.entrega))
        pdf.drawCentredString(x_centros[8], y, str(remision.restante))
        pdf.drawCentredString(x_centros[9], y, remision.status)

        # Línea final bajo la fila
        line_y = y - (8 * (max(num_lineas_entregas, num_lineas_concepto) - 1)) - 10
        pdf.line(30, line_y, width - 40, line_y)

        # Mover cursor
        y -= altura_fila + 2

    # Términos y Condiciones
    y -= 10
    y = verificar_pagina(pdf, y, margen=100)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Términos y Condiciones:")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y - 15, "• La descarga del producto corre a cuenta del cliente.")
    pdf.drawString(40, y - 30, "• Este documento no representa una factura.")
    pdf.drawString(40, y - 45, "• Los productos entregados deben ser revisados en el momento de la entrega.")

    # Código QR
    qr_image = generate_qr(cotizacion.direccion_entrega)
    qr_image.seek(0)
    qr_reader = ImageReader(qr_image)

    qr_width = 75
    qr_height = 75
    qr_x = width - qr_width - 10
    qr_y = 10

    if cotizacion.direccion_entrega != "Pendiente":
        pdf.drawImage(qr_reader, qr_x, qr_y, width=qr_width, height=qr_height, preserveAspectRatio=True, mask='auto')

    # Firma del Arquitecto
    firma_width = 180
    firma_height = 90
    firma_x = (width / 3) - (firma_width / 2)
    firma_y = y - 125

    firma_path = "static/img/firma.png"
    pdf.drawImage(ImageReader(firma_path), firma_x, firma_y - 50, width=firma_width, height=firma_height, preserveAspectRatio=True, mask='auto')

    pdf.drawCentredString(width / 3, y - 150, "Arq. Luis Alberto Hernández Lara.")

    # Firma del Cliente
    pdf.line(width - 200, y - 130, width - 40, y - 130)
    pdf.drawCentredString(width - 120, y - 145, "Firma del Cliente")

    # Guardar el PDF
    pdf.save()
    return response