from django.db import models

# Create your models here.
class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10)
    email = models.EmailField(max_length=50)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre