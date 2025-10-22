
from funddata import FundData
from requests import request
from ucitsfunds import UCITS_FUNDS
import json

class MyWebApi:
    def __init__(self, main_api_url: str = "http://localhost:8080"):
        self.main_api_url = main_api_url
        

    def add_fund(self, fund_data: FundData):
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

    def get_fund(self, bloomberg_ticker: str):
        print(f"Getting fund data for ticker: {bloomberg_ticker}")

        response = request(
            method="GET",
            url=f"{self.main_api_url}/funds/{bloomberg_ticker}"
        )

        if response.status_code == 200:
            fund_info = response.json()
            print(f"Fund data retrieved successfully: {fund_info}")
            return fund_info
        else:
            print(f"Error, returned: {response.status_code}; failed: {response}")
            return None


if __name__ == "__main__":
    api = MyWebApi()
    for f in UCITS_FUNDS:
        api.add_fund(f)

    
    test_response = api.get_fund("V3AA")
    print("fetched response:", test_response)
    # fetched response: {'id': 2, 'bloombergTicker': 'V3AA', 'fundName': 'Vanguard ESG Global All Cap UCITS Acc', 'morningStarId': 'F000016OZH', 'isin': 'IE00BNG8L278', 'priceRecords': []}
    

