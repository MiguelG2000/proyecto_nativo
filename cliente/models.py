from django.db import models

# Create your models here.
class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre