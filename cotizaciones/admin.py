from django.contrib import admin
from cotizaciones.models import (
    Cotizaciones,
    CotizacionProduct,
    Remisiones,
    Entregas,
    ConfiguracionIVA
    )

# Register your models here.
admin.site.register(Cotizaciones)
admin.site.register(CotizacionProduct)
admin.site.register(Remisiones)
admin.site.register(Entregas)

@admin.register(ConfiguracionIVA)
class ConfiguracionIVAAdmin(admin.ModelAdmin):
    list_display = ('porcentaje_iva',)
