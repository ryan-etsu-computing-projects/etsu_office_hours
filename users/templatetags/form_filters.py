from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Template filter to add a CSS class to a form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})