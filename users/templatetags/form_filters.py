from django import template
import re

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Template filter to add a CSS class to a form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='remove_prepended_junk')
def remove_prepended_junk(field, junk_to_remove):
    """
    Remove crap like "Department of" from "Department of Computing"
    Usage: {{ profile.department|remove_prepended_junk:"Department of" }}
    """
    junk_to_remove = junk_to_remove.lower()
    junk_len = len(junk_to_remove)
    if field.lower().startswith(junk_to_remove) and junk_len < len(field):
        return field[junk_len:].lstrip()
    else:
        return field
