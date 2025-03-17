from django import forms
from .models import Product
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'categoria', 'volumen', 'unidad', 'inventario', 'precio_general', 'precio_distribuidor', 'thumbnail']

    def clean_volumen(self):
        volumen = self.cleaned_data.get('volumen')
        if volumen is not None and volumen < 0:
            raise ValidationError("El volumen debe ser un número positivo.")
        return volumen

    def clean_inventario(self):
        inventario = self.cleaned_data.get('inventario')
        if inventario is not None and inventario < 0:
            raise ValidationError("El inventario debe ser un número positivo.")
        return inventario

    def clean_precio_general(self):
        precio = self.cleaned_data.get('precio_general')
        if precio is not None and precio < 0:
            raise ValidationError("El precio general debe ser un número positivo.")
        return precio

    def clean_precio_distribuidor(self):
        precio = self.cleaned_data.get('precio_distribuidor')
        if precio is not None and precio < 0:
            raise ValidationError("El precio de distribuidor debe ser un número positivo.")
        return precio