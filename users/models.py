from django.db import models

# Create your models here.
class Event(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=False)

    def __str__(self):
        return self.nombre