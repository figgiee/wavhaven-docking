from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using bracket notation.
    
    Args:
        dictionary: The dictionary to look up from
        key: The key to look up
        
    Returns:
        The value for the key if it exists, otherwise None
    """
    return dictionary.get(key) 