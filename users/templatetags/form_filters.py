from django.contrib.auth.models import Group
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Template filter to add a CSS class to a form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='print_preferred_name')
def print_preferred_name(profile):
    name = ""
    if profile.honorific: name += f"{profile.honorific} "
    if profile.preferred_name: name += f"{profile.preferred_name}"
    else: name += f"{profile.user.get_full_name()}"
    return name

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

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False
    return group in user.groups.all()

@register.simple_tag(name='newline_split_on_tokens')
def newline_split_on_tokens(text, tokens_str):
    result = text
    tokens = list(tokens_str)
    for token in tokens:
        if token in text:
            print(f"token {token} found")
            split_text = text.split(token)
            stripped = [ t.strip() for t in split_text ]
            result = mark_safe('<br>'.join(stripped))
            break
    return result