from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def startswith(string, start):
    if string and start:
        return string.startswith(start)
    return False