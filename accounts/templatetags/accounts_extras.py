from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    return bool(user and user.is_authenticated and user.groups.filter(name=group_name).exists())
