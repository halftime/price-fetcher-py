
from dataclasses import dataclass
from datetime import date as datetype


@dataclass
class SeriesData: # 'open': 95.88, 'high': 96.67, 'low': 93.46, 'close': 95.33, 'volume': 1222392, 'nav': 95.38799, 'totalReturn': 95.38799
    open : float | None = None
    high : float | None = None
    low : float | None = None
    close : float | None = None
    volume : int | None = None
    date : datetype | None = None

    nav : float | None = None # sometimes missing in the data
    totalReturn : float | None = None # sometimes missing in the data
    previousClose : float | None = None # sometimes missing in the data