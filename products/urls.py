from django.urls import path, include
from products.views import (
    products_view,
    create_product,
    update_product,
    delete_product,
    )

urlpatterns = [
    path("list/", products_view, name="products"),
    path("create/", create_product, name="create_product"),
    path("update/<int:product_id>/", update_product , name="update_product"),
    path("delete/<int:product_id>/", delete_product, name="delete_product"),
]