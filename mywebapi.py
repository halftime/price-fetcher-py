
from funddata import FundInfo
from requests import request
from seriesdata import MorningStarSeries
from pricerecord import PriceRecord
from ucitsfunds import UCITS_FUNDS
from datetime import date, datetime
import json
import httpx
import asyncio
from typing import Any

class MyWebApi: # http://192.168.129.222:8080 # http://ignc.dev:8080 , returns not local denied
    def __init__(
        self,
        main_api_url: str = "http://192.168.129.222:8080",
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
        retry_delay_seconds: float = 0.75,
    ):
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds))
        self.main_api_url = main_api_url
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response | None:
        url = f"{self.main_api_url}{endpoint}"

        if "json" in kwargs:
            kwargs["json"] = self._to_jsonable(kwargs["json"])

        for attempt in range(self.max_retries + 1):
            try:
                return await self.client.request(method=method, url=url, **kwargs)
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout) as ex:
                is_last_attempt = attempt >= self.max_retries
                print(
                    f"Timeout calling {url} (attempt {attempt + 1}/{self.max_retries + 1}): {ex}"
                )
                if is_last_attempt:
                    return None
                await asyncio.sleep(self.retry_delay_seconds)
            except httpx.RequestError as ex:
                print(f"Request error calling {url}: {ex}")
                return None

        return None

    def _to_jsonable(self, value: Any) -> Any:
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: self._to_jsonable(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._to_jsonable(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._to_jsonable(item) for item in value)
        return value

    def _to_date(self, value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            if "T" in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            return date.fromisoformat(value)
        raise ValueError(f"Unsupported date value type: {type(value)}")

    async def close(self):
        await self.client.aclose()

    async def add_fund(self, fund_data: FundInfo):
        print(f"Adding fund data: {fund_data}")

        response = await self._request("POST", "/addfund", json=fund_data.__dict__)

        if response is None:
            print("Error adding fund: request failed after retries.")
            return

        if response.status_code == 201:
            print("Fund added successfully.")
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")

    async def get_sorted_pricerecs(self, bloomberg_ticker: str) -> list[PriceRecord]:
        print(f"Getting price records for ticker: {bloomberg_ticker}")

        response = await self._request("GET", f"/prices/{bloomberg_ticker}")

        if response is None:
            print("Error retrieving price records: request failed after retries.")
            return []

        if response.status_code == 200:
            pricerecords_info = response.json()
            print(f"Price records retrieved successfully: {pricerecords_info}")
            parsed_records: list[PriceRecord] = []
            for pr in pricerecords_info:
                payload = dict(pr)
                payload["date"] = self._to_date(payload["date"])
                parsed_records.append(PriceRecord(**payload))
            sorted_records = sorted(parsed_records, key=lambda x: x.date) # sort by date ascending, oldest first
            return sorted_records
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")
            return []

    async def add_price_record(self, pricerecord: PriceRecord) -> httpx.Response:
        print(f"Adding price record: {pricerecord}")

        response = await self._request("POST", "/addpricerecord", json=pricerecord.__dict__)

        if response is None:
            print("Error adding price record: request failed after retries.")
            return httpx.Response(status_code=599, request=httpx.Request("POST", f"{self.main_api_url}/addpricerecord"))

        print(">> http Response status code:", response.status_code)
        return response


    async def get_fund(self, bloomberg_ticker: str) -> FundInfo | None:
        print(f"Getting fund data for ticker: {bloomberg_ticker}")

        response = await self._request("GET", f"/funds/{bloomberg_ticker}")

        if response is None:
            print("Error retrieving fund: request failed after retries.")
            return None

        if response.status_code == 200:
            fund_info = response.json()
            print(f"Fund data retrieved successfully: {fund_info}")
            return FundInfo(**fund_info)
        else:
            print(f"Error, returned: {response.status_code}; failed: {response.content}")
            return None


    
    async def get_price_record(self, boomberg_ticker:str, date:date):
        print(f"Getting price record for ticker: {boomberg_ticker} on date: {date}")

        response = await self._request("GET", f"/pricerecord/{boomberg_ticker}/{date.isoformat()}")

        if response is None:
            print("Error retrieving price record: request failed after retries.")
            return None

        if response.status_code == 200:
            pricerecord_info = response.json()
            print(f"Price record retrieved successfully: {pricerecord_info}")
            payload = dict(pricerecord_info)
            payload["date"] = self._to_date(payload["date"])
            return PriceRecord(**payload)
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
    await api.close()

if __name__ == "__main__":
    asyncio.run(mainasync())
    input("Press Enter to exit...")