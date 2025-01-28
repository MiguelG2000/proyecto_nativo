import os

from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django_otp.plugins.otp_email.conf import settings

# Create your models here.
class Product(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=False)
    descripcion = models.CharField(max_length=100, blank=True, null=False)
    categoria = models.CharField(max_length=50, blank=True, null=False)
    volumen = models.FloatField(blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=False)
    inventario = models.IntegerField(blank=True, null=True)
    precio_general = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=False)
    precio_distribuidor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=False)
    imagen = models.ImageField(upload_to='images_products/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbs', blank=True, null=True, editable=False)

    def __str__(self):
        return self.nombre

    '''def save(self, *args, **kwargs):
        if not self.make_thumbnail():
            raise Exception("No se pudo crear la miniatura")

        super(Product, self).save(*args, **kwargs)

    def make_thumbnail(self):
        imagen = Image.open(self.image)
        thumbnail_size = 75, 75
        imagen.thumbnail(thumbnail_size)

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        imagen.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True'''
