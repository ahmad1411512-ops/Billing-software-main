from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    return f'{amount:,.2f}'


@register.filter
def money0(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    if amount == amount.to_integral_value():
        return f'{int(amount):,}'
    return f'{amount:,.2f}'
