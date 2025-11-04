from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter para obtener un valor de diccionario usando clave dinámica"""
    return dictionary.get(key, 0)