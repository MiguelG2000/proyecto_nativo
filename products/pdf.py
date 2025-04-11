from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from datetime import datetime
from .models import Product


def product_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_productos_faltantes.pdf"'

    # Crear el documento con SimpleDocTemplate para mejor manejo de flujo
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Lista de elementos a añadir al PDF
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        alignment=1,  # Centrado
        spaceAfter=12
    )

    style_normal = styles['Normal']
    style_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        alignment=1
    )

    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Italic'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1
    )

    # Encabezado con logo y fecha
    header_data = []

    # Intentar añadir el logo
    try:
        logo = Image("static/img/logo.png", width=80, height=50)
        logo.hAlign = 'LEFT'
        header_data.append(logo)
    except:
        header_data.append(Paragraph("", style_normal))

    # Añadir fecha
    fecha = datetime.now().strftime('%d/%m/%Y')
    fecha_text = Paragraph(f"<para align='right'>Fecha: {fecha}</para>", style_normal)
    header_data.append(fecha_text)

    # Crear tabla de encabezado para alinear logo y fecha
    header_table = Table([header_data], colWidths=[doc.width / 2, doc.width / 2])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Título
    title = Paragraph("Reporte de Productos Faltantes", style_title)
    elements.append(title)
    elements.append(Spacer(1, 5))

    # Línea separadora como tabla para mantener coherencia
    line = Table([['']], colWidths=[doc.width])
    line.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.black)
    ]))
    elements.append(line)
    elements.append(Spacer(1, 15))

    # Obtener productos faltantes
    products = Product.objects.filter(otro=False, inventario__lte=11)

    # Si no hay productos, mostrar un mensaje
    if not products:
        elements.append(Paragraph("No hay productos con inventario menor o igual a 11.", style_normal))
    else:
        # Datos para la tabla
        data = [["Producto", "Inventario"]]
        for product in products:
            data.append([product.nombre, str(product.inventario)])

        # Crear tabla responsiva
        # El ancho total es el ancho del documento menos los márgenes
        table_width = doc.width
        col_widths = [table_width * 0.75, table_width * 0.25]  # Distribución de columnas

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Estilo del encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Estilo para las filas de datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternar colores en filas para mejor legibilidad
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.whitesmoke]),
        ]))

        elements.append(table)

    # Añadir espacio
    elements.append(Spacer(1, 20))

    # Nota al pie
    nota = Paragraph("Este reporte muestra los productos con inventario menor o igual a 11.", style_footer)
    elements.append(nota)
    elements.append(Spacer(1, 15))

    # Línea final y pie de página
    footer_line = Table([['']], colWidths=[doc.width])
    footer_line.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey)
    ]))
    elements.append(footer_line)
    elements.append(Spacer(1, 10))

    footer = Paragraph("Nativo_TA - Reporte generado automáticamente.", style_normal)
    elements.append(footer)

    # Construir el PDF
    doc.build(elements)
    return response


def product_inventory(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_inventario_completo.pdf"'

    # Crear el documento
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    # Lista de elementos
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,
        spaceAfter=12
    )

    style_normal = styles['Normal']
    style_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        alignment=1
    )

    # Encabezado con logo y fecha
    header_data = []

    # Intentar añadir el logo
    try:
        logo = Image("static/img/logo.png", width=80, height=50)
        logo.hAlign = 'LEFT'
        header_data.append(logo)
    except:
        header_data.append(Paragraph("", style_normal))

    # Añadir fecha
    fecha = datetime.now().strftime('%d/%m/%Y')
    fecha_text = Paragraph(f"<para align='right'>Fecha: {fecha}</para>", style_normal)
    header_data.append(fecha_text)

    # Crear tabla de encabezado
    header_table = Table([header_data], colWidths=[doc.width / 2, doc.width / 2])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Título
    title = Paragraph("Reporte de Inventario Completo", style_title)
    elements.append(title)
    elements.append(Spacer(1, 5))

    # Línea separadora
    line = Table([['']], colWidths=[doc.width])
    line.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.black)
    ]))
    elements.append(line)
    elements.append(Spacer(1, 15))

    # Obtener todos los productos
    products = Product.objects.filter(otro=False).order_by('-inventario')

    # Si no hay productos, mostrar un mensaje
    if not products:
        elements.append(Paragraph("No hay productos registrados en el inventario.", style_normal))
    else:
        # Datos para la tabla
        data = [["Producto", "Inventario"]]
        for product in products:
            data.append([product.nombre, str(product.inventario)])

        # Crear tabla responsiva
        table_width = doc.width
        col_widths = [table_width * 0.75, table_width * 0.25]

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Estilo del encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Estilo para las filas de datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternar colores en filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.whitesmoke]),
        ]))

        elements.append(table)

    # Añadir espacio
    elements.append(Spacer(1, 20))

    # Línea final y pie de página
    footer_line = Table([['']], colWidths=[doc.width])
    footer_line.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.lightgrey)
    ]))
    elements.append(footer_line)
    elements.append(Spacer(1, 10))

    footer = Paragraph("Nativo_TA - Reporte generado automáticamente.", style_normal)
    elements.append(footer)

    # Construir el PDF
    doc.build(elements)
    return response