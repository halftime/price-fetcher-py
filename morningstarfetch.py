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

client = httpx.AsyncClient()

async def collect_morningstar_maasToken(tickerQuery:str="0P0001I3S0") -> str: # just collecting the token
    url = f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart"
    headers = {
        "Accept": "application/json",
        "Origin": "https://global.morningstar.com",
        "Referer": f"https://global.morningstar.com/en-gb/investments/etfs/{tickerQuery}/chart",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "x-api-requestid": str(uuid.uuid4())
    }

    response = await client.get(url, headers=headers)

    json_data = str(response.text)
    if 'maasToken:"' in json_data:
        try:
            return json_data.split('maasToken:"')[1].split('"')[0]
        except Exception:
            raise Exception("maasToken was not found in the response")
    raise Exception("Failed to fetch data")


async def fetch_morningstar_history(tickerQuery:str, maasBearerToken:str, startDate:date, endDate:date=date.today()) -> list[MorningStarSeries]:
    url = f"https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries?query={tickerQuery}:totalReturn,nav,open,high,low,close,volume,previousClose"
    url += "&frequency=d" # frequency = 1/d : daily, m : monthly
    url += f"&startDate={startDate}&endDate={endDate}"
    url += "&trackMarketData=3.6.5&instid=DOTCOM"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0",
        "Authorization": f"Bearer {maasBearerToken}",
    }

    response = await client.get(url, headers=headers)

    if response.status_code == 200:
        series = [MorningStarSeries(**item) for item in response.json()[0]["series"]]
        return sorted(series, key=lambda x: x.date, reverse=False) # sort by date ascending, oldest first
    return []


async def mainasync():
    maas_token = await collect_morningstar_maasToken()
    print ("Fetched maas bearer token:", maas_token)
    api = MyWebApi()

    for f in UCITS_FUNDS:
        await api.add_fund(f)

        fetch_start_date : date = date(1900, 1, 1)

        existing_pricerecs : list[PriceRecord] = await api.get_sorted_pricerecs(f.bloombergTicker)
        if existing_pricerecs:
            print (f"{f.bloombergTicker} ; existing price records found: ", len(existing_pricerecs), "; latest date:", existing_pricerecs[-1].date)
            fetch_start_date : date = existing_pricerecs[-1].date
        series = await fetch_morningstar_history(f.morningStarId, maas_token, startDate=fetch_start_date)

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

        print(f"{f.bloombergTicker} ; price records fetched: ", len(pricerecords))
        for pr in pricerecords:
            httpx_response : httpx.Response = await api.add_price_record(pr)
            if (httpx_response.status_code == 201):
                print(f"Added price record for {f.bloombergTicker} on {pr.date}")
            elif (httpx_response.status_code == 409):
                print(f"Price record for {f.bloombergTicker} on {pr.date} already exists")
            else:
                print(f"Failed to add price record for {f.bloombergTicker} on {pr.date}: {httpx_response.status_code} - {httpx_response.content}")

if __name__ == "__main__":
    asyncio.run(mainasync())