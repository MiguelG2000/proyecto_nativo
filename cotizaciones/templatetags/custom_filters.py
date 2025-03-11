from decimal import Decimal
from io import BytesIO

from django import template
import base64

register = template.Library()

@register.filter(name='moneda')
def moneda(value):
    if isinstance(value, Decimal):
        return "{:,.2f}".format(value)
    return value