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
    imagen = models.ImageField(upload_to='images_products/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbs', blank=True, null=True, editable=False)

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

    def save(self, *args, **kwargs):
    # Primero guardar el producto para que tenga un ID válido
        super(Product, self).save(*args, **kwargs)

    # Si hay una imagen, generar el thumbnail
        if self.imagen:
            self.make_thumbnail()

    def make_thumbnail(self):
        self.imagen.open()  # Asegurarse de que la imagen está abierta
        imagen = Image.open(self.imagen)

        thumbnail_size = (75, 75)
        imagen.thumbnail(thumbnail_size)

        # Obtener nombre y extensión del archivo
        thumb_name, thumb_extension = os.path.splitext(self.imagen.name)
        thumb_extension = thumb_extension.lower()

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Tipo de archivo no reconocido

        # Crear un archivo temporal en memoria
        temp_thumb = BytesIO()
        imagen.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # Guardar la miniatura con un nuevo nombre
        thumb_filename = f"{thumb_name}_thumb{thumb_extension}"
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        # Guardar nuevamente para actualizar la miniatura
        super(Product, self).save(update_fields=['thumbnail'])

        return True
