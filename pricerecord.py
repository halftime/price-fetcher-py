from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass
class PriceRecord:
    """
    Python dataclass equivalent of the provided C# PriceRecord.
    """
    fundId: int
    date: date
    close: float = 0
    open: float = 0
    high: float = 0
    low: float = 0
    nav: float = 0
    volume: int = 0