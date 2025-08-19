from django import template

register = template.Library()


@register.filter
def mask_cnib(value: str) -> str:
    if not value:
        return ""
    return "*" * max(len(value) - 4, 0) + value[-4:]
