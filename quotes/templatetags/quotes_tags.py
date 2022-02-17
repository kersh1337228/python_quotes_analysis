from django import template


register = template.Library()


@register.inclusion_tag('form.html')
def form_tag(**kwargs):
    return kwargs


@register.inclusion_tag('quote.html')
def quote_tag(**kwargs):
    return kwargs

@register.inclusion_tag('pagination.html')
def pagination_tag(**kwargs):
    return kwargs
