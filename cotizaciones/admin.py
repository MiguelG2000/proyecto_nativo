from django.contrib import admin
from cotizaciones.models import Cotizaciones, CotizacionProduct, Remisiones

# Register your models here.
admin.site.register(Cotizaciones)
admin.site.register(CotizacionProduct)
admin.site.register(Remisiones)
