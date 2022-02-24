from django import template


register = template.Library()


# Simple form on page
@register.inclusion_tag('form.html')
def form_tag(**kwargs):
    return kwargs


# Quotes for single share
@register.inclusion_tag('quote.html')
def quote_tag(**kwargs):
    return kwargs


# Quotes list pagination
@register.inclusion_tag('pagination.html')
def pagination_tag(**kwargs):
    return kwargs
