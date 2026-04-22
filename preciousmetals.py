from dataclasses import dataclass
from fund import PreciousMetal


@dataclass
class PreciousMetals:
    xag: PreciousMetal
    xau: PreciousMetal
    xpt: PreciousMetal

    @classmethod
    def example(cls) -> "PreciousMetals":
        return cls(
            xag=PreciousMetal(
                symbol="XAG",
                name="Silver",
            ),
            xau=PreciousMetal(
                symbol="XAU",
                name="Gold",
            ),
            xpt=PreciousMetal(
                symbol="XPT",
                name="Platinum",
                
            ),
        )


PRECIOUS_METALS_LIST: list[PreciousMetal] = [m for m in PreciousMetals.example().__dict__.values()]
