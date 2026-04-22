import asyncio
from datetime import date, timedelta 
from pprint import pformat

import httpx
from bullionstarreply import BullionStarReply

from preciousmetals import PRECIOUS_METALS_LIST
from mywebapi import MyWebApi
from pricerecord import MinimalPriceRecord

client = httpx.AsyncClient()


def _log(from_index: str, message: str) -> None:
    print(f"[BullionStar][{from_index}] {message}")

async def fetch_bullionstar_spot_price(fromIndex:str, toIndex:str="EUR", period:str="MAX") -> dict[date, float]:
    url = f"https://services.bullionstar.com/spot-chart/getChart?product=false&productId=0&productTo=false&productIdTo=0&fromIndex={fromIndex}&toIndex={toIndex}&period={period}&width=1000&height=1000&timeZoneId=Europe%2FBrussels&weightUnit=tr_oz"
    resultDict: dict[date, float] = {}
    _log(fromIndex, f"Fetching spot price data for {fromIndex}->{toIndex} period={period}")
    _log(fromIndex, f"Request URL: {url}")
    response = await client.get(url)
    _log(fromIndex, f"HTTP status: {response.status_code}")
    if response.status_code == 200:
        payload = response.json()
        _log(fromIndex, "Raw JSON payload:")
        print(pformat(payload, width=140))

        bullionstar_reply = BullionStarReply(**payload)
        _log(fromIndex, f"Parsed bullionstar reply: {bullionstar_reply}")
        _log(fromIndex, f"Parsed reply fields:\n{pformat(bullionstar_reply.__dict__, width=140)}")

        if not bullionstar_reply.dataSeries:
            _log(fromIndex, "No dataSeries points were returned.")
            return resultDict

        days_diff = (bullionstar_reply.endDate - bullionstar_reply.startDate).days
        _log(fromIndex, f"Start date: {bullionstar_reply.startDate}")
        _log(fromIndex, f"End date: {bullionstar_reply.endDate}")
        _log(fromIndex, f"days diff: {days_diff}")

        delta_d: int = bullionstar_reply.dataSeries[-1]["d"] - bullionstar_reply.dataSeries[0]["d"]
        _log(fromIndex, f"delta d: {delta_d}")

        for dv in bullionstar_reply.dataSeries:
            approx_offset_days = round(dv["d"] * days_diff / delta_d) if delta_d else 0
            approx_date = bullionstar_reply.startDate + timedelta(days=approx_offset_days)
            resultDict[approx_date] = dv["v"]

        _log(fromIndex, f"Completed fetch with {len(resultDict)} mapped rows.")
    else:
        _log(fromIndex, f"Response body:\n{response.text}")

    return resultDict

        #return response.json().get("data", [])
    
# https://services.bullionstar.com/spot-chart/getChart?product=false&productId=0&productTo=false&productIdTo=0&fromIndex=XAG&toIndex=EUR&period=MAX&width=1000&height=1000&timeZoneId=Europe%2FBrussels&weightUnit=tr_oz


async def main():
    api = MyWebApi()
    try:
        for metal in PRECIOUS_METALS_LIST:
            results = await fetch_bullionstar_spot_price(fromIndex=metal.symbol)
            added_metal = await api.add_precious_metal(metal)
            investment_id = added_metal.id if (added_metal is not None and added_metal.id is not None) else metal.id
            if investment_id is None:
                _log(metal.symbol, "No investment id available, skipping price record sync")
                continue
            for record_date, price in results.items():
                pr = MinimalPriceRecord(symbol=metal.symbol, price=price, date=record_date)
                await api.add_price_record(pr)
    finally:
        await client.aclose()
        await api.close()


if __name__ == "__main__":
    asyncio.run(main())
