from datetime import date
from ucitsfunds import UCITS_FUNDS
from mywebapi import MyWebApi
from pricerecord import MinimalPriceRecord
from morningstarclient import MorningstarClient
import httpx
import asyncio


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


async def _sync_price_records_to_api(
    api: MyWebApi, ticker: str, records: list[MinimalPriceRecord]
) -> None:
    print(f"{ticker} ; price records to sync: {len(records)}")
    for pr in records:
        httpx_response: httpx.Response = await api.add_price_record(pr)
        if httpx_response.status_code == 201:
            print(f"Added price record for {ticker} on {pr.date}")
        elif httpx_response.status_code == 409:
            print(f"Price record for {ticker} on {pr.date} already exists")
        else:
            print(f"Failed to add price record for {ticker} on {pr.date}: {httpx_response.status_code} - {httpx_response.content}")


async def morningstarasync():
    ms_client = MorningstarClient()
    try:
        api = MyWebApi()
        try:
            for f in UCITS_FUNDS:
                await api.add_fund(f)
                api_existing_pricerecs: list[MinimalPriceRecord] = await api.get_sorted_pricerecs(f.symbol)
                latest_api_date = _coerce_to_date(api_existing_pricerecs[-1].date) if api_existing_pricerecs else None
                if latest_api_date:
                    print(f"{f.symbol} ; API latest date: {latest_api_date}")

                fetch_start_date = latest_api_date or date(1900, 1, 1)
                source_series = await ms_client.fetch_history(f.morningStarId, start_date=fetch_start_date)

                cached_pricerecords = [
                    MinimalPriceRecord(symbol=f.symbol, price=s.close, date=s.date)
                    for s in source_series
                    if s.close is not None
                ]
                if latest_api_date:
                    cached_pricerecords = [pr for pr in cached_pricerecords if pr.date > latest_api_date]

                await _sync_price_records_to_api(api, f.symbol, cached_pricerecords)
        finally:
            await api.close()
    finally:
        await ms_client.close()

if __name__ == "__main__":
    #input("Enter to start Morningstar fetch and API sync...")
    asyncio.run(morningstarasync())
