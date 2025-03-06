from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from cotizaciones.models import Cotizaciones, CotizacionProduct
from datetime import datetime

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
    fecha_dt = datetime.strptime(str(fecha), "%Y-%m-%d")  # Convertir a datetime
    dia_semana = dias_semana[fecha_dt.strftime("%A")]  # Obtener día
    dia = fecha_dt.strftime("%d")  # Obtener el número del día
    mes = meses[fecha_dt.strftime("%B")]  # Obtener mes
    anio = fecha_dt.strftime("%Y")  # Obtener año

    return f"{dia_semana}, {dia} de {mes} del {anio}"

def generate_quote_pdf(request, id):
    # Obtener la cotización y los productos relacionados
    cotizacion = Cotizaciones.objects.get(id=id)
    productos = CotizacionProduct.objects.filter(cotizacion_id=cotizacion, product_id__otro=False)
    productosPer = CotizacionProduct.objects.filter(cotizacion_id=cotizacion, product_id__otro=True)

    # Formatear fechas manualmente
    fecha_cotizacion = formatear_fecha(cotizacion.fecha)
    fecha_validez = formatear_fecha(cotizacion.fecha_propuesta)

    # Configurar la respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.id}.pdf"'

    # Crear el objeto PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Logo bien proporcionado
    logo_path = "static/img/logo.png"
    pdf.drawImage(ImageReader(logo_path), 40, height - 80, width=100, height=50, preserveAspectRatio=True, mask='auto')

    # Datos de la empresa alineados con el logo
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(160, height - 50, "GRUPO NATIVO")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(160, height - 65, "20 Poniente Sur #550B CP. 29070 | Tuxtla Gutiérrez, Chiapas.")
    pdf.drawString(160, height - 80, "             nativo.tu.mx@gmail.com | 961 693 66 44")

    # Ajuste para centrar mejor la sección de cotización
    cotizacion_x = width - 250

    # Datos del Cliente a la izquierda
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, height - 130, "Datos del cliente:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 145, f"Cliente: {cotizacion.cliente}")
    pdf.drawString(40, height - 160, "Ing. Fernando")
    pdf.drawString(40, height - 175, "Tuxtla Gutiérrez, Chiapas.")

    # Cotización más centrada
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(cotizacion_x, height - 130, f"COTIZACIÓN: {cotizacion.id}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(cotizacion_x, height - 145, f"Fecha: {fecha_cotizacion}")
    pdf.drawString(cotizacion_x, height - 160, f"Válido hasta: {fecha_validez}")

    # Mensaje de introducción
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, height - 200, "Estimado cliente, por medio del presente, le hago entrega de la cotización solicitada. Puede corroborar a detalle la presente cotización.")
    pdf.drawString(40, height -215, "Cualquier duda favor de contactarnos, con gusto se la resolvemos.")

    y = height - 240

    # *** TABLA DE PRODUCTOS NORMALES (si existen) ***
    if productos.exists():
        pdf.setFont("Helvetica-Bold", 8)
        col_positions = [40, 100, 160, 320, 450, 550]
        headers = ["Unidad", "Cantidad", "Descripción", "P.U.", "Total"]

        for i in range(len(headers)):
            pdf.drawCentredString((col_positions[i] + col_positions[i + 1]) / 2, y, headers[i])

        # Línea superior de la tabla (corregida)
        pdf.line(40, y + 8, width - 40, y + 8)  # Ajustar mejor la posición de la línea

        # *** CORREGIR LÍNEA DEBAJO DE LOS ENCABEZADOS ***
        pdf.line(40, y - 5, width - 40, y - 5)
        y -= 20

        pdf.setFont("Helvetica", 8)
        for producto in productos:
            pdf.drawCentredString((col_positions[0] + col_positions[1]) / 2, y, producto.product_id.unidad)
            pdf.drawCentredString((col_positions[1] + col_positions[2]) / 2, y, str(producto.cantidad))
            pdf.drawCentredString((col_positions[2] + col_positions[3]) / 2, y, producto.product_id.nombre)
            pdf.drawCentredString((col_positions[3] + col_positions[4]) / 2, y, f"${producto.phistorico}")
            pdf.drawCentredString((col_positions[4] + col_positions[5]) / 2, y, f"${producto.subtotal}")

            # Línea horizontal para separar filas (corregida)
            pdf.line(40, y - 5, width - 40, y - 5)
            y -= 20  # Espaciado entre filas

    # *** TABLA DE PRODUCTOS PERSONALIZADOS ***
    if productosPer.exists():
        y -= 10  # Espacio antes de la tabla
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(40, y, "Productos Personalizados")
        y -= 15

        # Ajustar mejor las posiciones de las columnas
        col_positions = [40, 140, 180, 210, 240, 270, 320, 380, 450, 550]
        encabezados = ["Concepto", "Cantidad", "Largo", "Ancho", "Alto", "Vol. Pza", "P.U.", "Vol. Total", "Total"]

        pdf.setFont("Helvetica-Bold", 8)

        # Dibujar encabezados centrados
        for i in range(len(encabezados)):
            pdf.drawCentredString((col_positions[i] + col_positions[i + 1]) / 2, y, encabezados[i])

        # Línea superior de la tabla (corregida)
        pdf.line(40, y + 8, width - 40, y + 8)  # Ajustar mejor la posición de la línea

        # *** CORREGIR LÍNEA DEBAJO DE LOS ENCABEZADOS ***
        pdf.line(40, y - 5, width - 40, y - 5)
        y -= 20

        pdf.setFont("Helvetica", 8)
        for producto in productosPer:
            pdf.drawCentredString((col_positions[0] + col_positions[1]) / 2, y, producto.product_id.nombre[:22])
            pdf.drawCentredString((col_positions[1] + col_positions[2]) / 2, y, str(producto.cantidad))
            pdf.drawCentredString((col_positions[2] + col_positions[3]) / 2, y, f"{producto.product_id.largo:.2f}")
            pdf.drawCentredString((col_positions[3] + col_positions[4]) / 2, y, f"{producto.product_id.ancho:.2f}")
            pdf.drawCentredString((col_positions[4] + col_positions[5]) / 2, y, f"{producto.product_id.alto:.2f}")
            pdf.drawCentredString((col_positions[5] + col_positions[6]) / 2, y, f"{producto.product_id.volumen:.2f}")
            pdf.drawCentredString((col_positions[6] + col_positions[7]) / 2, y, f"${producto.phistorico:.2f}")
            pdf.drawCentredString((col_positions[7] + col_positions[8]) / 2, y, f"{producto.product_id.volumen_total:.2f}")
            pdf.drawCentredString((col_positions[8] + col_positions[9]) / 2, y, f"${producto.subtotal:.2f}")

            # Línea horizontal para separar filas (corregida)
            pdf.line(40, y - 5, width - 40, y - 5)
            y -= 20  # Espaciado entre filas

    # Subtotales alineados con términos y condiciones
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(400, y - 10, "Envío a " + f"{cotizacion.servicio_envio}:")
    pdf.drawString(520, y - 10, f"${cotizacion.costo_envio}")

    pdf.drawString(400, y - 30, "Subtotal:")
    pdf.drawString(520, y - 30, f"${cotizacion.total}")

    pdf.drawString(400, y - 50, "I.V.A.:")
    pdf.drawString(520, y - 50, f"${cotizacion.iva}")

    pdf.drawString(400, y - 70, "Anticipo:")
    pdf.drawString(520, y - 70, f"${cotizacion.anticipo}")

    pdf.drawString(400, y - 90, "Total a pagar:")
    pdf.drawString(520, y - 90, f"${cotizacion.restante}")

    # Determinar la tasa de IVA aplicada
    iva_tasa = "8%" if cotizacion.iva_8 else "16%" if cotizacion.iva_16 else "0%"

    # Términos y condiciones
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(40, y - 10, "Términos y condiciones:")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(40, y - 25, f"• La tasa de IVA calculada es del {iva_tasa}.")
    pdf.drawString(40, y - 40, "• Precios sujetos a cambios sin previo aviso.")
    pdf.drawString(40, y - 55, "• No incluye descarga en obra.")
    pdf.drawString(40, y - 70, "• Este documento es de carácter informativo sin validez oficial.")

    # Tiempo de entrega alineado con términos
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(40, y - 100, "Tiempo de entrega:")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(40, y - 115, "1 o 2 días hábiles posteriores al pago total de la presente cotización.")
    pdf.drawString(40, y - 130, "Sin más por el momento, quedo a sus órdenes por cualquier duda o aclaración.")

    # Nombre del Arq alineado
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(width / 3, y - 160, "Arq. Luis Alberto Hernández Lara.")

    # Firma y "Recibí material completo"
    pdf.setFont("Helvetica", 9)
    firma_x = width - 200
    pdf.line(firma_x, y - 140, firma_x + 160, y - 140)
    pdf.drawCentredString(firma_x + 80, y - 155, "Firma del Cliente")
    pdf.drawCentredString(firma_x + 80, y - 170, "Recibí material completo")

    # Guardar el PDF
    pdf.save()
    return response
