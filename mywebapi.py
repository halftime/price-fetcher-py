
from funddata import FundData
from requests import request
import json

class MyWebApi:
    def __init__(self, main_api_url: str = "http://localhost:8080"):
        self.main_api_url = main_api_url
        

    def add_fund(self, fund_data: FundData):
        # Placeholder for adding fund data to the web API
        print(f"Adding fund data: {fund_data}")

        response = request(
            method="POST",
            url=f"{self.main_api_url}/addfund",
            json=fund_data.__dict__
        )

        if response.status_code == 201:
            print("Fund added successfully.")
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")


if __name__ == "__main__":
    testFund = FundData(
        ISIN="IE00B4L5Y983",
        FundName="iShares Core MSCI World UCITS ETF (Acc)",
        BloombergTicker="EUNL",
        MorningstarId="0P0001I3S"
    )

    api = MyWebApi()
    api.add_fund(testFund)



