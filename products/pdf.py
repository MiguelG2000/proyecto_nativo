from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image
from datetime import datetime
from .models import Product

def product_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_productos.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    logo_path = "static/img/logo.png"
    try:
        p.drawImage(logo_path, 40, height - 80, width=80, height=50, preserveAspectRatio=True, mask='auto')
    except:
        pass

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    fecha = datetime.now().strftime('%d/%m/%Y')
    p.drawString(width - 150, height - 50, f"Fecha: {fecha}")

    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.black)
    titulo = "Reporte de Productos Faltantes"
    titulo_width = p.stringWidth(titulo, "Helvetica-Bold", 20)
    p.drawString((width - titulo_width) / 2, height - 100, titulo)

    # Línea decorativa bajo el título
    p.setStrokeColor(colors.black)
    p.setLineWidth(2)
    p.line(50, height - 110, width - 50, height - 110)

    products = Product.objects.filter(otro=False, inventario__lte=11)

    data = [["Producto", "Inventario"]]
    for product in products:
        data.append([product.nombre, str(product.inventario)])

    table = Table(data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('ROWBACKGROUNDS', (1, -1), (-1, -1), [colors.lightgrey]),  # Filas alternas
        ('GRID', (0, 0), (-1, -1), 1, colors.gray)
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, (width - 400) / 2, height - 350)

    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.gray)
    nota = "Este reporte muestra los productos con inventario menor o igual a 11."
    nota_width = p.stringWidth(nota, "Helvetica-Oblique", 10)
    p.drawString((width - nota_width) / 2, 120, nota)

    p.setStrokeColor(colors.lightgrey)
    p.line(50, 80, width - 50, 80)  # Línea separadora
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.black)
    p.drawString(50, 60, "Nativo_TA - Reporte generado automáticamente.")

    # Guardar el PDF
    p.showPage()
    p.save()
    return response

def product_inventory(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_productos.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Agregar Logo
    logo_path = "static/img/logo.png"
    try:
        p.drawImage(logo_path, 40, height - 80, width=80, height=50, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Fecha en la parte superior derecha
    p.setFont("Helvetica", 12)
    fecha = datetime.now().strftime('%d/%m/%Y')
    p.drawString(width - 120, height - 50, f"Fecha: {fecha}")

    # Título centrado
    p.setFont("Helvetica-Bold", 18)
    titulo = "Reporte de Productos"
    titulo_width = p.stringWidth(titulo, "Helvetica-Bold", 18)
    p.drawString((width - titulo_width) / 2, height - 90, titulo)

    # Línea decorativa bajo el título
    p.setStrokeColor(colors.black)
    p.setLineWidth(2)
    p.line(50, height - 100, width - 50, height - 100)

    # Obtener productos
    products = Product.objects.filter(otro=False)

    # Definir datos de la tabla
    data = [["Producto", "Inventario"]]
    for product in products:
        data.append([product.nombre, str(product.inventario)])

    # Definir tabla con anchos fijos
    table = Table(data, colWidths=[350, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.gray)
    ]))

    # Dibujar tabla (más arriba para evitar desbordes)
    table.wrapOn(p, width, height)
    table.drawOn(p, 80, height - 620)

    # Línea separadora y footer
    p.setStrokeColor(colors.lightgrey)
    p.line(50, 80, width - 50, 80)
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.black)
    p.drawString(50, 60, "Nativo_TA - Reporte generado automáticamente.")

    # Guardar PDF
    p.showPage()
    p.save()
    return response
