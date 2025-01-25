# pharma/templatetags/carton_tags.py
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_cart(context):
    # Logique pour obtenir le panier
    return "Panier vide"
