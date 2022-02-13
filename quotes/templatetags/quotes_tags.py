from django import template


register = template.Library()


@register.inclusion_tag('form.html')
def form_tag(**kwargs):
    return kwargs
