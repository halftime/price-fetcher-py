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
    close: float
    open: float
    high: float
    low: float
    nav: float
    volume: int
    nonzeroprice: Optional[float] = None # derived
    