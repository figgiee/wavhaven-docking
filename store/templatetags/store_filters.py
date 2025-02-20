from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Get a value from a dictionary using a key."""
    return dictionary.get(key) 