from django.contrib import admin
from products.models import Product, Categorias, Unidades
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'inventario')
    list_filter = ('otro', 'unidad')

admin.site.register(Product, ProductAdmin)
admin.site.register(Categorias)
admin.site.register(Unidades)
