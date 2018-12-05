from decimal import Decimal

DEFAULT_ZERO = Decimal('0.00000000')

def to_decimal(number):
    return Decimal(number).quantize(DEFAULT_ZERO)
