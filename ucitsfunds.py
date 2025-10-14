
from dataclasses import dataclass
from funddata import FundData

@dataclass
class UCITSFunds:
    vwce: FundData
    v3aa: FundData
    iwda: FundData
    rbot: FundData
    volt: FundData
    sxrs: FundData

    @classmethod
    def example(cls) -> "UCITSFunds":
        return cls(
            vwce=FundData(
                ticker="VWCE",
                name="Vanguard FTSE All-World ETF UCITS Acc",
                morningstarId="0P0001I3S0",
                ISIN="IE00BK5BQT80",
            ),
            v3aa=FundData(
                ticker="V3AA",
                name="Vanguard ESG Global All Cap UCITS Acc",
                morningstarId="F000016OZH",
                ISIN="IE00BNG8L278",
            ),

            iwda=FundData(
                ticker="IWDA",
                name="iShares Core MSCI World UCITS Acc",
                morningstarId="0P0000MLIH",
                ISIN="IE00B4L5Y983"
            ),

            sxrs=FundData(
                ticker="SXRS",
                name="iShares Diversified Commodity Swap UCITS Acc",
                morningstarId="0P0001D6YY",
                ISIN="IE00BDFL4P12"
         ),

            volt=FundData(
                ticker="VOLT",
                name="WisdomTree Battery Solutions UCITS Acc",
                morningstarId="F000014VZD",
                ISIN="IE00BKLF1R75",
            ),

            rbot=FundData(
                ticker="RBOT",
                name="Ishares Automation & Robotics UCITS Acc",
                morningstarId="F00000XPTP",
                ISIN="IE00BYZK4552"
        )
        )
        
            

UCITS_FUNDS = UCITSFunds.example()