
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
                BloombergTicker="VWCE",
                FundName="Vanguard FTSE All-World ETF UCITS Acc",
                MorningstarId="0P0001I3S0",
                ISIN="IE00BK5BQT80",
            ),
            v3aa=FundData(
                BloombergTicker="V3AA",
                FundName="Vanguard ESG Global All Cap UCITS Acc",
                MorningstarId="F000016OZH",
                ISIN="IE00BNG8L278",
            ),

            iwda=FundData(
                BloombergTicker="IWDA",
                FundName="iShares Core MSCI World UCITS Acc",
                MorningstarId="0P0000MLIH",
                ISIN="IE00B4L5Y983"
            ),

            sxrs=FundData(
                BloombergTicker="SXRS",
                FundName="iShares Diversified Commodity Swap UCITS Acc",
                MorningstarId="0P0001D6YY",
                ISIN="IE00BDFL4P12"
         ),

            volt=FundData(
                BloombergTicker="VOLT",
                FundName="WisdomTree Battery Solutions UCITS Acc",
                MorningstarId="F000014VZD",
                ISIN="IE00BKLF1R75",
            ),

            rbot=FundData(
                BloombergTicker="RBOT",
                FundName="Ishares Automation & Robotics UCITS Acc",
                MorningstarId="F00000XPTP",
                ISIN="IE00BYZK4552"
        )
        )
        
            



UCITS_FUNDS = [f for f in UCITSFunds.example().__dict__.values()]