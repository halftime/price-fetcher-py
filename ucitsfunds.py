
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
                bloombergTicker="VWCE",
                fundName="Vanguard FTSE All-World ETF UCITS Acc",
                morningStarId="0P0001I3S0",
                iSIN="IE00BK5BQT80",
                fundId=1
            ),
            v3aa=FundInfo(
                bloombergTicker="V3AA",
                fundName="Vanguard ESG Global All Cap UCITS Acc",
                morningStarId="F000016OZH",
                iSIN="IE00BNG8L278",
                fundId=2
            ),

            iwda=FundInfo(
                bloombergTicker="IWDA",
                fundName="iShares Core MSCI World UCITS Acc",
                morningStarId="0P0000MLIH",
                iSIN="IE00B4L5Y983",
                fundId=3
            ),

            sxrs=FundInfo(
                bloombergTicker="SXRS",
                fundName="iShares Diversified Commodity Swap UCITS Acc",
                morningStarId="0P0001D6YY",
                iSIN="IE00BDFL4P12",
                fundId=4
         ),

            volt=FundInfo(
                bloombergTicker="VOLT",
                fundName="WisdomTree Battery Solutions UCITS Acc",
                morningStarId="F000014VZD",
                iSIN="IE00BKLF1R75",
                fundId=5
            ),

            rbot=FundInfo(
                bloombergTicker="RBOT",
                fundName="Ishares Automation & Robotics UCITS Acc",
                morningStarId="F00000XPTP",
                iSIN="IE00BYZK4552",
                fundId=6
            ),
        )
        
            



UCITS_FUNDS : list[FundInfo] = [f for f in UCITSFunds.example().__dict__.values()]