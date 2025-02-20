from django.db import models
from django.db.transaction import mark_for_rollback_on_error

from cliente.models import Cliente
from products.models import Product

# Create your models here.
class Cotizaciones(models.Model):
    id = models.CharField(max_length=10, primary_key=True, unique=True, blank=False, null=False)
    fecha = models.CharField(max_length=100, blank=False, null=False)
    fecha_propuesta = models.CharField(max_length=100, blank=False, null=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, blank=False, null=False, default='Pendiente')
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    restante = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=20, null=False, default='No')

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
        self.cal_restante()

    def cal_restante(self):
        self.restante = self.total - self.anticipo
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
