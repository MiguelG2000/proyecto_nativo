from django.db import models

from cliente.models import Cliente
from products.models import Product
from decimal import Decimal


# Create your models here.
class Cotizaciones(models.Model):
    id = models.CharField(max_length=10, primary_key=True, unique=True, blank=False, null=False)
    fecha = models.DateField(auto_now=False, auto_now_add=True)
    fecha_propuesta = models.DateField(auto_now=False, auto_now_add=True)
    servicio_envio = models.CharField(max_length=100, blank=False, null=True, default=None)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) # Este total es el total sin IVA por cuestiones programaticas lo decidimos dejar así.
    total_Civa = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, blank=False, null=False, default='Pendiente')
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=20, null=False, default='No')
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    iva_8 = models.BooleanField(default=False)
    iva_16 = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        # Si es una nueva cotización y no tiene ID, generar uno automáticamente
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
        iva_porcentaje = Decimal('0.16') if self.iva_16 else Decimal('0.08') if self.iva_8 else Decimal('0')
        total_decimal = Decimal(str(self.total))
        costo_envioDecimal = Decimal(str(self.costo_envio))
        # Calcular el IVA
        self.iva = total_decimal * iva_porcentaje
        self.total_Civa = total_decimal + self.iva + costo_envioDecimal

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
