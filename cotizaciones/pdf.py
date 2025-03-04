from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from cotizaciones.models import Cotizaciones, CotizacionProduct

def generate_quote_pdf(request, id):
    # Obtener la cotización y los productos relacionados
    cotizacion = Cotizaciones.objects.get(id=id)
    productos = CotizacionProduct.objects.filter(cotizacion_id=cotizacion)

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
    pdf.drawString(160, height - 50, "NATIVO GRUPO")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(160, height - 65, "20 Poniente Sur #550B CP. 29070 | Tuxtla Gutiérrez, Chiapas.")
    pdf.drawString(160, height - 80, "nativo.tu.mx@gmail.com | 961 693 66 44")

    # Ajuste para centrar mejor la sección de cotización
    cotizacion_x = width - 250

    # Datos del Cliente a la izquierda
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, height - 130, "Datos del cliente:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 145, "Cliente: Presforza")
    pdf.drawString(40, height - 160, "Ing. Fernando")
    pdf.drawString(40, height - 175, "Tuxtla Gutiérrez, Chiapas.")

    # Cotización más centrada
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(cotizacion_x, height - 130, f"COTIZACIÓN: {cotizacion.id}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(cotizacion_x, height - 145, f"Fecha: {cotizacion.fecha}")
    pdf.drawString(cotizacion_x, height - 160, f"Válido hasta: {cotizacion.fecha_propuesta}")

    # Mensaje de introducción
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 200, "Estimado cliente, por medio del presente, le hago entrega de la cotización solicitada.")

    # Coordenadas de la tabla
    y = height - 240
    col_positions = [40, 100, 160, 320, 450, 550]  # Posiciones de las columnas
    row_height = 20

    # Dibujar la tabla con solo líneas horizontales
    pdf.setFont("Helvetica-Bold", 10)

    # Dibujar encabezados centrados
    headers = ["Unidad", "Cantidad", "Descripción", "P.U.", "Total"]
    for i in range(len(headers)):
        pdf.drawCentredString((col_positions[i] + col_positions[i + 1]) / 2, y, headers[i])

    pdf.line(40, y + 10, width - 40, y + 10)  # Línea superior de la tabla
    y -= row_height

    pdf.setFont("Helvetica", 10)
    for producto in productos:
        pdf.drawCentredString((col_positions[0] + col_positions[1]) / 2, y, producto.product_id.unidad)
        pdf.drawCentredString((col_positions[1] + col_positions[2]) / 2, y, str(producto.cantidad))
        pdf.drawCentredString((col_positions[2] + col_positions[3]) / 2, y, producto.product_id.nombre)
        pdf.drawCentredString((col_positions[3] + col_positions[4]) / 2, y, f"${producto.phistorico}")
        pdf.drawCentredString((col_positions[4] + col_positions[5]) / 2, y, f"${producto.subtotal}")

        pdf.line(40, y + 10, width - 40, y + 10)  # Solo líneas horizontales
        y -= row_height

    pdf.line(40, y + 10, width - 40, y + 10)  # Línea inferior de la tabla

    # Subtotales alineados con términos y condiciones
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(400, y - 10, "Subtotal:")
    pdf.drawString(520, y - 10, f"${cotizacion.total}")

    pdf.drawString(400, y - 30, "I.V.A.:")
    pdf.drawString(520, y - 30, f"${cotizacion.iva}")

    pdf.drawString(400, y - 50, "Total a pagar:")
    pdf.drawString(520, y - 50, f"${cotizacion.total_Civa}")

    # Términos y condiciones alineados
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(40, y - 10, "Términos y condiciones:")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(40, y - 25, "• La tasa de IVA calculada es del 16%.")
    pdf.drawString(40, y - 40, "• Precios sujetos a cambios sin previo aviso.")
    pdf.drawString(40, y - 55, "• No incluye descarga en obra.")
    pdf.drawString(40, y - 70, "• Este documento es de carácter informativo sin validez oficial.")

    # Tiempo de entrega alineado con términos
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(40, y - 100, "Tiempo de entrega:")
    pdf.setFont("Helvetica", 7)
    pdf.drawString(40, y - 115, "1 Día hábil posterior al pago total de la presente cotización.")
    pdf.drawString(40, y - 130, "Sin más por el momento, quedo a sus órdenes por cualquier duda o aclaración.")

    # Nombre del Arq alineado
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(width / 3, y - 160, "Arq. Luis Alberto Hernández Lara.")

    # Firma y "Recibí material completo" centrados
    pdf.setFont("Helvetica", 9)
    firma_x = width - 200
    pdf.line(firma_x, y - 140, firma_x + 160, y - 140)
    pdf.drawCentredString(firma_x + 80, y - 155, "Firma del Cliente")
    pdf.drawCentredString(firma_x + 80, y - 170, "Recibí material completo")

    # Guardar el PDF
    pdf.save()
    return response
