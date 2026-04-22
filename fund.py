
from dataclasses import dataclass, field

@dataclass
class Investment:
    id: int | None = None
    symbol: str = ""
    name : str = ""

    def __post_init__(self):
        if self.id is not None and (not isinstance(self.id, int) or self.id <= 0):
            raise ValueError("Id must be a positive integer")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")
        
        self.name = self.name.strip().lower()
        self.symbol = self.symbol.strip().upper()
        
        if len(self.symbol) > 10:
            raise ValueError("Symbol cannot be longer than 10 characters")
        
        if len(self.name) > 100:
            raise ValueError("Name cannot be longer than 100 characters")
        
        


@dataclass
class PreciousMetal(Investment):
    def __post_init__(self):
        super().__post_init__()
        if not self.name:
            raise ValueError("name cannot be empty")


@dataclass
class FundInfo(Investment):

    morningStarId: str = ""
    isin: str = ""  # Accept API field 'isin' as alias for 'iSIN'

    def __post_init__(self):
        super().__post_init__()

        if not self.morningStarId:
            raise ValueError("morningStarId cannot be empty")
        if not self.isin:
            raise ValueError("isin cannot be empty")
