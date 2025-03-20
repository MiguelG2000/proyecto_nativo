from django.urls import path, include

from cotizaciones.views import (
    quotes_view,
    details_view,
    create_quote,
    update_quote,
    delete_quote,
    add_product_to_quote,
    add_custom_product_to_quote,
    delete_product_from_quote, view_remission,
)
from cotizaciones.pdf import generate_quote_pdf
from cotizaciones.remisiones import generate_remission_pdf

urlpatterns = [
    path('', quotes_view, name='list_quotes'),
    path('details/<str:id>/', details_view, name='details'),
    path('create/',create_quote,name='create_quote' ),
    path('update/<str:id>/',update_quote,name='update_quote' ),
    path('delete/<str:id>/',delete_quote,name='delete_quote' ),
    path('details/<str:id>/add-product/', add_product_to_quote, name='add_product_to_quote'),
    path('details/<str:id>/add-custom-product/', add_custom_product_to_quote, name='add_custom_product_to_quote'),
    path('details/<int:id>/delete-product/', delete_product_from_quote, name='delete_product_from_quote'),
    path('cotizacion/<str:id>/pdf/', generate_quote_pdf, name='generate_quote_pdf'),
    path('remission/<str:id>/', view_remission, name='view_remission'),
    path('remission/<str:id>/pdf/', generate_remission_pdf, name='generate_remission_pdf'),


]