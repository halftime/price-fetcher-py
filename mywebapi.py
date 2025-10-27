
from funddata import FundInfo
from requests import request
from seriesdata import MorningStarSeries
from pricerecord import PriceRecord
from ucitsfunds import UCITS_FUNDS
from datetime import date
import json
import httpx
import asyncio

class MyWebApi:
    def __init__(self, main_api_url: str = "http://localhost:8080"):
        self.main_api_url = main_api_url
        self.client = httpx.AsyncClient()

    async def add_fund(self, fund_data: FundInfo):
        print(f"Adding fund data: {fund_data}")

        response = await self.client.post(
                url=f"{self.main_api_url}/addfund",
                json=fund_data.__dict__
            )

        if response.status_code == 201:
            print("Fund added successfully.")
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")

    async def add_price_record(self, pricerecord: PriceRecord) -> bool:
        print(f"Adding price record: {pricerecord}")

        response = await self.client.post(
            url=f"{self.main_api_url}/addpricerecord",
            json=pricerecord.__dict__
        )

        if response.status_code == 201:
            #print("Price record added successfully.")
            return True
        else:
            #print(f"Error, returned: {response.status_code}; failed: {response.content}")
            return False
    

    async def get_fund(self, bloomberg_ticker: str) -> FundInfo | None:
        print(f"Getting fund data for ticker: {bloomberg_ticker}")

        response = await self.client.get(f"{self.main_api_url}/funds/{bloomberg_ticker}")

        if response.status_code == 200:
            fund_info = response.json()
            print(f"Fund data retrieved successfully: {fund_info}")
            return FundInfo(**fund_info)
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")
            return None


    
    async def get_price_record(self, boomberg_ticker:str, date:date):
        print(f"Getting price record for ticker: {boomberg_ticker} on date: {date}")

        response = await self.client.get(f"{self.main_api_url}/prices/{boomberg_ticker}/{date.isoformat()}")

        if response.status_code == 200:
            pricerecord_info = response.json()
            print(f"Price record retrieved successfully: {pricerecord_info}")
            return PriceRecord(**pricerecord_info)
        else:
            print(f"Error, returned: {response.status_code}; failed: {response}")
            return None


async def mainasync():
    api = MyWebApi()

    # run add_fund concurrently for all funds
    tasks = [asyncio.create_task(api.add_fund(f)) for f in UCITS_FUNDS]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for fund, res in zip(UCITS_FUNDS, results):
        if isinstance(res, Exception):
            print(f"Failed to add {fund}: {res}")
        else:
            print(f"Added {fund}")


    test_response = await api.get_fund("V3AA")
    print("fetched response:", test_response)
    # fetched response: {'id': 2, 'bloombergTicker': 'V3AA', 'fundName': 'Vanguard ESG Global All Cap UCITS Acc', 'morningStarId': 'F000016OZH', 'isin': 'IE00BNG8L278', 'priceRecords': []}

if __name__ == "__main__":
    asyncio.run(mainasync())
    input("Press Enter to exit...")