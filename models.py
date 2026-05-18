from decimal import Decimal, ROUND_DOWN

def format_decimal(value):
    return Decimal(value).quantize(Decimal("0.0000000001"), rounding=ROUND_DOWN)
