import os

from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import BooleanField

# Create your models here.
class Product(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=False)
    descripcion = models.CharField(max_length=100, blank=True, null=False)
    categoria = models.CharField(max_length=50, blank=True, null=False)
    largo = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    ancho = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    alto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=0)
    volumen = models.FloatField(blank=True, null=True, default=0)
    volumen_total = models.FloatField(blank=True, null=True, default=0)
    unidad = models.CharField(max_length=50, blank=True, null=False)
    inventario = models.IntegerField(blank=True, null=True)
    precio_general = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=False)
    precio_distribuidor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    otro = BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def update_volumen(self):
        #Calcular volumen por pieza
        self.volumen = self.largo * self.ancho * self.alto

        #Calcular volumen total
        from cotizaciones.models import CotizacionProduct
        cotizaciones = CotizacionProduct.objects.filter(product_id=self)
        self.volumen_total = sum(self.volumen * cotizacion.cantidad for cotizacion in cotizaciones)
        self.save()

class Categorias(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=False)

    def __str__(self):
        return self.nombre

class Unidades(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=False)

    def __str__(self):
        return self.nombre
