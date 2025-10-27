
from dataclasses import dataclass

@dataclass
class FundInfo:
    fundId: int
    bloombergTicker: str
    fundName: str
    morningStarId: str
    iSIN: str
