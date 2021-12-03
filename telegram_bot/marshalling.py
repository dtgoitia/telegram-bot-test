import decimal
from typing import Any

from cattr import structure  # noqa
from cattr import unstructure  # noqa
from cattr import register_structure_hook, register_unstructure_hook


def structure_decimal(raw: str, _: Any) -> decimal.Decimal:
    return decimal.Decimal(raw)


def unstructure_decimal(data: decimal.Decimal) -> str:
    return str(data)


register_structure_hook(decimal.Decimal, structure_decimal)
register_unstructure_hook(decimal.Decimal, unstructure_decimal)
