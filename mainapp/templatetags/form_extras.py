# mainapp/templatetags/form_extras.py
from django import template

register = template.Library()

@register.filter(name='add_attrs')
def add_attrs(field, css):
    attrs = {}
    for pair in css.split(','):
        key, value = pair.split('=')
        attrs[key.strip()] = value.strip()
    
    # Aplica los atributos al campo
    for attr, val in attrs.items():
        field.field.widget.attrs[attr] = val

    return field
