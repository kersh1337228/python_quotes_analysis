from django import template


register = template.Library()


@register.inclusion_tag('strategy_tag.html')
def strategy_tag(**kwargs):
    return kwargs


@register.inclusion_tag('log_tag.html')
def log_tag(**kwargs):
    return kwargs
