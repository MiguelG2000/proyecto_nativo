from django.urls import path, include
from .views import (
    products_view,
    create_product,
    update_product,
    delete_product,
    category_unit,
    create_category,
    delete_category,
    create_unit,
    delete_unit,
    )
from .pdf import product_report

urlpatterns = [
    path("list/", products_view, name="products"),
    path("create/", create_product, name="create_product"),
    path("update/<int:product_id>/", update_product , name="update_product"),
    path("delete/<int:product_id>/", delete_product, name="delete_product"),
    path("report/", product_report, name="product_report"),
    path("category/", category_unit, name="category_unit"),
    path("category/create/", create_category, name="create_category"),
    path("category/delete/<int:category_id>/", delete_category, name="delete_category"),
    path("unit/create/", create_unit, name="create_unit"),
    path("unit/delete/<int:unit_id>/", delete_unit, name="delete_unit"),
]