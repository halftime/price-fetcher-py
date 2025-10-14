
from dataclasses import dataclass

@dataclass
class FundData:
    ticker: str
    name: str
    morningstarId: str
    ISIN: str


