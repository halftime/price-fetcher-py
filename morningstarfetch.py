import requests
import uuid
from datetime import date, timedelta
from requests import Session
from seriesdata import MorningStarSeries
from ucitsfunds import UCITS_FUNDS
from funddata import FundInfo
from mywebapi import MyWebApi
from pricerecord import PriceRecord
import httpx
import asyncio

async def collect_morningstar_maasToken(tickerQuery:str="0P0001I3S0") -> str: # just collecting the token
    url = f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart"
    headers = {
        "Accept": "application/json",
        "Origin": "https://global.morningstar.com",
        "Referer": f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "x-api-requestid": str(uuid.uuid4())
    }

    async with httpx.AsyncClient() as reqSession:
        response = await reqSession.get(url, headers=headers)

    json_data = str(response.text)
    if 'maasToken:"' in json_data:
        try:
            return json_data.split('maasToken:"')[1].split('"')[0]
        except Exception:
            raise Exception("maasToken was not found in the response")
    raise Exception("Failed to fetch data")


async def fetch_morningstar_history(tickerQuery:str, maasBearerToken:str, startDate:str="1900-01-01", endDate:str=date.today().isoformat()) -> list[MorningStarSeries]:
    url = f"https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries?query={tickerQuery}:totalReturn,nav,open,high,low,close,volume,previousClose"
    url += "&frequency=d" # frequency = 1/d : daily, m : monthly
    url += f"&startDate={startDate}&endDate={endDate}"
    url += "&trackMarketData=3.6.5&instid=DOTCOM"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "Authorization": f"Bearer {maasBearerToken}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        return [MorningStarSeries(**item) for item in response.json()[0]["series"]]
    return []


async def mainasync():
    maas_token = await collect_morningstar_maasToken()
    print ("Fetched maas bearer token:", maas_token)
    api = MyWebApi()

    for f in UCITS_FUNDS:
        await api.add_fund(f)
        series = await fetch_morningstar_history(f.morningStarId, maas_token)
        pricerecords : list[PriceRecord] = []

        for s in series:
            pricerecords.append(PriceRecord(
                fundId=f.fundId,
                date=s.date,
                open=s.open or 0,
                high=s.high or 0,
                low=s.low or 0,
                close=s.close or 0,
                volume=s.volume or 0,
                nav=s.nav or 0
            ))

        print("Executing asyncio tasks: ", len(pricerecords))
        tasklist = [asyncio.create_task(api.add_price_record(pr)) for pr in pricerecords]
        await asyncio.gather(*tasklist, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(mainasync())