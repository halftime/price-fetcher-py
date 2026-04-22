
from dataclasses import dataclass
from funddata import FundInfo

@dataclass
class UCITSFunds:
    vwce: FundInfo
    v3aa: FundInfo
    iwda: FundInfo
    rbot: FundInfo
    volt: FundInfo
    sxrs: FundInfo

    @classmethod
    def example(cls) -> "UCITSFunds":
        return cls(
            vwce=FundInfo(
                symbol="VWCE",
                name="Vanguard FTSE All-World ETF UCITS Acc",
                morningStarId="0P0001I3S0",
                iSIN="IE00BK5BQT80"
            ),
            v3aa=FundInfo(
                symbol="V3AA",
                name="Vanguard ESG Global All Cap UCITS Acc",
                morningStarId="F000016OZH",
                iSIN="IE00BNG8L278"
            ),

            iwda=FundInfo(
                symbol="IWDA",
                name="iShares Core MSCI World UCITS Acc",
                morningStarId="0P0000MLIH",
                iSIN="IE00B4L5Y983"
            ),

            sxrs=FundInfo(
                symbol="SXRS",
                name="iShares Diversified Commodity Swap UCITS Acc",
                morningStarId="0P0001D6YY",
                iSIN="IE00BDFL4P12"
         ),

            volt=FundInfo(
                symbol="VOLT",
                name="WisdomTree Battery Solutions UCITS Acc",
                morningStarId="F000014VZD",
                iSIN="IE00BKLF1R75"
            ),

            rbot=FundInfo(
                symbol="RBOT",
                name="Ishares Automation & Robotics UCITS Acc",
                morningStarId="F00000XPTP",
                iSIN="IE00BYZK4552"
            ),
        )
        
            



UCITS_FUNDS : list[FundInfo] = [f for f in UCITSFunds.example().__dict__.values()]