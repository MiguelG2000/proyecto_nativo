from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from rich.filesize import decimal

from cotizaciones.models import Cotizaciones, CotizacionProduct
from datetime import datetime
from .views import generate_qr
from .models import ConfiguracionIVA

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

buffer = BytesIO()
c = canvas.Canvas(buffer, pagesize=letter)

def formatear_fecha(fecha):
    fecha_dt = datetime.strptime(str(fecha), "%Y-%m-%d")
    dia_semana = dias_semana[fecha_dt.strftime("%A")]
    dia = fecha_dt.strftime("%d")
    mes = meses[fecha_dt.strftime("%B")]
    anio = fecha_dt.strftime("%Y")
    return f"{dia_semana}, {dia} de {mes} del {anio}"

def formato_moneda(valor):
    return "${:,.2f}".format(valor)

def verificar_pagina(pdf, y, margen=100):
    """Verifica si hay espacio suficiente en la página para continuar dibujando elementos."""
    if y < margen:  # Si el espacio es insuficiente, generar nueva página
        pdf.showPage()  # Crear nueva página
        agregar_encabezado(pdf)  # Redibujar encabezado
        return letter[1] - 160  # Reiniciar la posición en la nueva página
    return y


def agregar_encabezado(pdf):
    """Dibuja el encabezado en cada nueva página."""
    logo_path = "static/img/logo.png"
    pdf.drawImage(ImageReader(logo_path), 40, letter[1] - 120, width=200, height=100, preserveAspectRatio=True, mask='auto')

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(260, letter[1] - 50,"                        GRUPO NATIVO")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(260, letter[1] - 65, "20 Poniente Sur #550B CP. 29070 | Tuxtla Gutiérrez, Chiapas.")
    pdf.drawString(260, letter[1] - 80, "                nativo.tu.mx@gmail.com | 961 693 66 44")

def generate_quote_pdf(request, id):
    # Obtener la cotización y los productos relacionados
    cotizacion = Cotizaciones.objects.get(id=id)
    productos = CotizacionProduct.objects.filter(cotizacion_id=cotizacion, product_id__otro=False)
    productosPer = CotizacionProduct.objects.filter(cotizacion_id=cotizacion, product_id__otro=True)

    fecha_cotizacion = formatear_fecha(cotizacion.fecha)
    fecha_validez = formatear_fecha(cotizacion.fecha_propuesta)
    fecha_entrega = formatear_fecha(cotizacion.fecha_entrega)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    agregar_encabezado(pdf)

    y = height - 240

    # Datos del Cliente a la izquierda
    y = verificar_pagina(pdf, y)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(40, height - 130, "Datos del cliente:")
    y = verificar_pagina(pdf, y)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, height - 145, f"Cliente: {cotizacion.cliente}")
    pdf.drawString(40, height - 160, f"Telefono: {cotizacion.telefono}")
    if cotizacion.status == "Aceptado":
        pdf.drawString(40, height - 175, f"Dirección de entrega: {cotizacion.direccion_entrega}")

    # Definir la posición de alineación a la derecha
    margen_derecho = width - 40  # Ajusta el margen derecho según lo necesites

    # Cotización alineada a la derecha
    y = verificar_pagina(pdf, y)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(margen_derecho, height - 130, f"COTIZACIÓN: {cotizacion.id}")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(margen_derecho, height - 145, f"Fecha: {fecha_cotizacion}")
    pdf.drawRightString(margen_derecho, height - 160, f"Válido hasta: {fecha_validez}")

    # Mensaje de introducción
    y = verificar_pagina(pdf, y)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(40, height - 200, "Estimado cliente, por medio del presente, le hago entrega de la cotización solicitada.")
    pdf.drawString(40, height - 210, "Puede corroborar a detalle la presente cotización. Cualquier duda favor de contactarnos.")

# *** TABLA DE PRODUCTOS NORMALES (si existen) ***
    if productos.exists():
        pdf.setFont("Helvetica-Bold", 8)
        col_positions = [30, 120, 180, 360, 500, 580]
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
            y = verificar_pagina(pdf, y, margen = 150)
            pdf.drawCentredString((col_positions[0] + col_positions[1]) / 2, y, producto.product_id.unidad)
            pdf.drawCentredString((col_positions[1] + col_positions[2]) / 2, y, str(producto.cantidad))
            pdf.drawCentredString((col_positions[2] + col_positions[3]) / 2, y, producto.product_id.nombre)
            pdf.drawCentredString((col_positions[3] + col_positions[4]) / 2, y, f"${producto.phistorico:,.2f}")
            pdf.drawCentredString((col_positions[4] + col_positions[5]) / 2, y, f"${producto.subtotal:,.2f}")

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
        col_positions = [30, 150, 190, 230, 270, 310, 350, 420, 500, 580]  # Ajustado
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
            y = verificar_pagina(pdf, y, margen = 150)
            pdf.drawCentredString((col_positions[0] + col_positions[1]) / 2, y, producto.product_id.nombre[:22])
            pdf.drawCentredString((col_positions[1] + col_positions[2]) / 2, y, str(producto.cantidad))
            pdf.drawCentredString((col_positions[2] + col_positions[3]) / 2, y, f"{producto.product_id.largo:,.2f}")
            pdf.drawCentredString((col_positions[3] + col_positions[4]) / 2, y, f"{producto.product_id.ancho:,.2f}")
            pdf.drawCentredString((col_positions[4] + col_positions[5]) / 2, y, f"{producto.product_id.alto:,.2f}")
            pdf.drawCentredString((col_positions[5] + col_positions[6]) / 2, y, f"{producto.product_id.volumen:,.2f}")
            pdf.drawCentredString((col_positions[6] + col_positions[7]) / 2, y, f"${producto.phistorico:,.2f}")
            pdf.drawCentredString((col_positions[7] + col_positions[8]) / 2, y, f"{producto.product_id.volumen_total:,.2f}")
            pdf.drawCentredString((col_positions[8] + col_positions[9]) / 2, y, f"${producto.subtotal:,.2f}")

            # Línea horizontal para separar filas (corregida)
            pdf.line(40, y - 5, width - 40, y - 5)
            y -= 20  # Espaciado entre filas

    # Subtotales
    y = verificar_pagina(pdf, y, margen=120)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(400, y - 10, "Envío a " + f"{cotizacion.servicio_envio}:")
    pdf.drawString(520, y - 10, formato_moneda(cotizacion.costo_envio))
    pdf.drawString(400, y - 30, "Subtotal:")
    pdf.drawString(520, y - 30, formato_moneda(cotizacion.total))
    pdf.drawString(400, y - 50, "I.V.A.:")
    pdf.drawString(520, y - 50, formato_moneda(cotizacion.iva))

    alineacion_x = 400

    if cotizacion.anticipo != 0:
        y = verificar_pagina(pdf, y, margen=120)
        pdf.drawString(alineacion_x, y - 70, "Anticipo:")
        pdf.drawString(520, y - 70, formato_moneda(cotizacion.anticipo))

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(alineacion_x, y - 90, "Total a pagar:")
        pdf.drawString(520, y - 90, formato_moneda(cotizacion.restante))
    else:
        y = verificar_pagina(pdf, y, margen=120)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(alineacion_x, y - 70, "Total a pagar:")
        pdf.drawString(520, y - 70, formato_moneda(cotizacion.restante))

    #Obtener el dato del atributo IVA y evitar errores
    config_iva = ConfiguracionIVA.objects.first()
    tasa_iva = config_iva.porcentaje_iva if config_iva else 0

    # Términos y condiciones
    y = verificar_pagina(pdf, y, margen=120)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(40, y - 10, "Términos y condiciones:")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(40, y - 20, f"• La tasa de IVA calculada es del {int(tasa_iva)}%.")
    pdf.drawString(40, y - 30, "• Precios sujetos a cambios sin previo aviso.")
    pdf.drawString(40, y - 40, "• No incluye descarga en obra.")
    pdf.drawString(40, y - 50, "• Este documento es de carácter informativo sin validez oficial.")
    pdf.drawString(40, y - 60, "• Condiciones de pago: Pago de contado.")

    # Tiempo de entrega alineado con términos
    pdf.setFont("Helvetica-Bold", 7)
    y = verificar_pagina(pdf, y, margen=120)
    pdf.drawString(40, y - 80, "Tiempo de entrega:")
    pdf.setFont("Helvetica", 7)
    if cotizacion.status == "Aceptado":
        pdf.drawString(40, y - 90, f"La entrega será el dia {fecha_entrega}, cubriendo el pago total de la cotización.")
        pdf.drawString(40, y - 100, "La descarga del producto corre a cuenta del cliente.")
        pdf.drawString(40, y - 110, "Sin más por el momento, quedo a sus órdenes por cualquier duda o aclaración.")
        y -= 20
    else:
        pdf.drawString(40, y - 90, "La descarga del producto corre a cuenta del cliente.")
        pdf.drawString(40, y - 100, "Sin más por el momento, quedo a sus órdenes por cualquier duda o aclaración.")
        y -= 20

    y = verificar_pagina(pdf, y, margen=120)
    # Ajustar la posición de la firma del arquitecto para que esté más arriba
    firma_width = 180  # Ancho de la firma
    firma_height = 90  # Altura de la firma
    firma_x = (width / 3) - (firma_width / 2)  # Centrar firma con el texto
    firma_y = y - 125  # Ajustar la altura para que quede más arriba

    # Dibujar firma del arquitecto
    firma_path = "static/img/firma.png"  # Cuando se tenga la firma, cambiar esta ruta
    pdf.drawImage(ImageReader(firma_path), firma_x, firma_y - 50, width=firma_width, height=firma_height,
                  preserveAspectRatio=True, mask='auto')

    # Dibujar nombre del arquitecto alineado con la firma
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(width / 3, y - 150, "Arq. Luis Alberto Hernández Lara.")

    # Ajustar la posición de la firma del cliente
    firma_x = width - 200
    firma_line_y = y - 130  # Subir la línea para la firma del cliente
    pdf.line(firma_x, firma_line_y, firma_x + 160, firma_line_y)
    pdf.drawCentredString(firma_x + 80, firma_line_y - 15, "Firma del Cliente")
    pdf.drawCentredString(firma_x + 80, firma_line_y - 30, "Recibí material completo")

    # Generar el código QR correctamente
    qr_image = generate_qr(cotizacion.direccion_entrega)
    qr_image.seek(0)  # Asegurar que BytesIO está en la posición inicial
    qr_reader = ImageReader(qr_image)  # Convertir el BytesIO en ImageReader

    # Definir el tamaño del QR
    qr_width = 75  # Ancho del QR
    qr_height = 75  # Alto del QR

    # Posición lo más pegada posible a la esquina inferior derecha
    qr_x = width - qr_width - 10  # 10px de margen derecho
    qr_y = 10  # 10px de margen inferior

    # Dibujar la imagen del QR en la posición fija
    if cotizacion.direccion_entrega != "Pendiente":
        pdf.drawImage(qr_reader, qr_x, qr_y, width=qr_width, height=qr_height, preserveAspectRatio=True, mask='auto')

    # Guardar el PDF
    pdf.save()
    return response