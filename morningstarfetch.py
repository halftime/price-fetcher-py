from datetime import date
from ucitsfunds import UCITS_FUNDS
from mywebapi import MyWebApi
from pricerecord import PriceRecord
from morningstarcache import MorningstarCache
from morningstarclient import MorningstarClient
import httpx
import asyncio

cache = MorningstarCache()


def _coerce_to_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        if "T" in value:
            return date.fromisoformat(value.split("T", 1)[0])
        return date.fromisoformat(value)
    raise ValueError(f"Unsupported date value type: {type(value)}")


async def mainasync():
    cache.init_schema()
    ms_client = MorningstarClient()
    maas_token: str | None = None

    try:
        maas_token = await ms_client.collect_maas_token()
        print ("Fetched maas bearer token:", maas_token)
    except Exception as ex:
        print(f"Morningstar unavailable, skipping fetch phase: {ex}")

    if maas_token:
        for f in UCITS_FUNDS:
            latest_cached_date = cache.get_latest_cached_date(f.bloombergTicker)
            fetch_start_date = latest_cached_date or date(1900, 1, 1)
            if latest_cached_date:
                print(f"{f.bloombergTicker} ; local cache latest date: {latest_cached_date}")

            series = await ms_client.fetch_history(f.morningStarId, maas_token, start_date=fetch_start_date)
            inserted_rows = cache.save_series(f.bloombergTicker, f.morningStarId, f.fundId, series)
            print(f"{f.bloombergTicker} ; stored/updated rows in local cache: {inserted_rows}")
    else:
        print("Using existing local cache only (no Morningstar updates this run).")

    api = MyWebApi()

    for f in UCITS_FUNDS:
        await api.add_fund(f)

        api_existing_pricerecs : list[PriceRecord] = await api.get_sorted_pricerecs(f.bloombergTicker)
        latest_api_date = _coerce_to_date(api_existing_pricerecs[-1].date) if api_existing_pricerecs else None
        if latest_api_date:
            print(f"{f.bloombergTicker} ; API latest date: {latest_api_date}")

        cached_pricerecords = cache.load_cached_pricerecords(f.bloombergTicker, f.fundId)
        if latest_api_date:
            cached_pricerecords = [pr for pr in cached_pricerecords if pr.date > latest_api_date]

        print(f"{f.bloombergTicker} ; price records read from local cache for API sync: {len(cached_pricerecords)}")
        for pr in cached_pricerecords:
            httpx_response : httpx.Response = await api.add_price_record(pr)
            if (httpx_response.status_code == 201):
                print(f"Added price record for {f.bloombergTicker} on {pr.date}")
            elif (httpx_response.status_code == 409):
                print(f"Price record for {f.bloombergTicker} on {pr.date} already exists")
            else:
                print(f"Failed to add price record for {f.bloombergTicker} on {pr.date}: {httpx_response.status_code} - {httpx_response.content}")

    await api.close()
    await ms_client.close()

if __name__ == "__main__":
    asyncio.run(mainasync())