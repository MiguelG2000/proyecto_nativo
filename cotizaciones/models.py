from django.db import models
from products.models import Product
from decimal import Decimal


# Create your models here.
class Cotizaciones(models.Model):
    id = models.CharField(max_length=10, primary_key=True, unique=True, blank=False, null=False)
    cliente = models.CharField(max_length=50, blank=False, null=True)
    telefono = models.IntegerField(blank=False, null=True)
    fecha = models.DateField(auto_now=False, auto_now_add=False)
    fecha_propuesta = models.DateField(auto_now=False, auto_now_add=False)
    fecha_entrega = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    direccion_entrega = models.CharField(max_length=50, default='Pendiente')
    servicio_envio = models.CharField(max_length=100, default="TGZ")
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Total sin IVA
    total_Civa = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, blank=False, null=False, default='Pendiente')
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=20, null=False, default='No')
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        # Generar ID automáticamente si es una nueva cotización
        if not self.id:
            last_quote = Cotizaciones.objects.order_by('-id').first()
            if last_quote:
                num = int(last_quote.id.replace('COT', '')) + 1
                self.id = f'COT{num:02d}'
            else:
                self.id = 'COT01'
        super().save(*args, **kwargs)

    def update_total(self):
        self.total = sum(item.subtotal for item in self.cotizaciones.all())
        self.save()

    def calcular_iva(self):
        # Obtener el IVA desde la configuración global (asumimos que hay solo un registro)
        configuracion = ConfiguracionIVA.objects.first()
        iva_porcentaje = Decimal(str(configuracion.porcentaje_iva)) / 100 if configuracion else Decimal('0.16')

        total_decimal = Decimal(str(self.total))
        costo_envio_decimal = Decimal(str(self.costo_envio))

        # Calcular IVA y total con IVA
        self.iva = total_decimal * iva_porcentaje
        self.total_Civa = total_decimal + self.iva + costo_envio_decimal

        anticipo_decimal = Decimal(str(self.anticipo))
        self.restante = self.total_Civa - anticipo_decimal
        self.save()

class CotizacionProduct(models.Model):
    cotizacion_id = models.ForeignKey(Cotizaciones, on_delete=models.CASCADE, related_name='cotizaciones')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    phistorico = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    usar_precio_distribuidor = models.BooleanField(default=False)

    def __str__(self):
        return f"Cotización {self.cotizacion_id.id} - Producto {self.product_id.nombre}"

    def save(self, *args, **kwargs):
        if self.product_id:
            precio_usado = self.product_id.precio_distribuidor if self.usar_precio_distribuidor else self.product_id.precio_general
            self.subtotal = self.cantidad * precio_usado
            self.phistorico = precio_usado  # Guardar el precio usado en el histórico

        super().save(*args, **kwargs)
        self.cotizacion_id.update_total()

class Remisiones(models.Model):
    cotizacion_id = models.ForeignKey(Cotizaciones, on_delete=models.CASCADE, related_name='remisiones')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    entrega = models.IntegerField(default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, blank=False, null=False, default='Pendiente')

    def actualizar_totales(self):
        # Sumar todas las entregas realizadas
        total_entregado = self.entregas.aggregate(total_entregado=models.Sum('cantidad_entregada'))['total_entregado'] or 0

        # Obtener la cantidad original del producto en la cotización
        cotizacion_producto = CotizacionProduct.objects.filter(
            cotizacion_id=self.cotizacion_id, product_id=self.product_id
        ).first()

        cantidad_cotizada = cotizacion_producto.cantidad if cotizacion_producto else 0

        # Calcular restante y actualizar status
        self.total = total_entregado
        self.restante = max(cantidad_cotizada - total_entregado, 0)
        self.status = 'Completado' if self.restante == 0 else 'Pendiente'
        self.save()

    def __str__(self):
        return f"Hoja de remisión de {self.cotizacion_id.id}"

class Entregas(models.Model):
    remision = models.ForeignKey(Remisiones, on_delete=models.CASCADE, related_name='entregas')
    cantidad_entregada = models.IntegerField()

    def __str__(self):
        return f"Entrega del producto: {self.remision.product_id.nombre}"

class ConfiguracionIVA(models.Model):
    porcentaje_iva = models.DecimalField(max_digits=5, decimal_places=2, default=16.00,
                                             help_text="Porcentaje de IVA (ejemplo: 8.00, 16.00)")
    def __str__(self):
        return f"IVA: {self.porcentaje_iva}%"

