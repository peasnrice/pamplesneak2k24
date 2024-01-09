from django import template

register = template.Library()


@register.filter
def possessive(name):
    if name.endswith("s"):
        return f"{name}'"
    else:
        return f"{name}'s"
