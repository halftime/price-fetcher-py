from bullionstarfetch import fetch_bullionstar_spot_price
from preciousmetals import PRECIOUS_METALS_LIST
from mywebapi import MyWebApi
from pricerecord import MinimalPriceRecord
from pricecache import PriceCache
from morningstarfetch import _coerce_to_date, _sync_price_records_to_api

price_cache = PriceCache()
price_cache.init_schema()


async def bullionstarasync():
    api = MyWebApi()
    try:
        for metal in PRECIOUS_METALS_LIST:
            ticker = metal.symbol
            latest_cached_date = price_cache.get_latest_cached_date(ticker)
            if latest_cached_date:
                print(f"{ticker} ; local cache latest date: {latest_cached_date}")

            metal_results = await fetch_bullionstar_spot_price(fromIndex=ticker)
            if not metal_results:
                print(f"{ticker} ; no BullionStar results returned")
                continue

            inserted_rows = price_cache.save_prices(ticker, metal_results)
            print(f"{ticker} ; stored/updated rows in local cache: {inserted_rows}")

            added_metal = await api.add_precious_metal(metal)
            investment_id = added_metal.Id if (added_metal is not None and added_metal.Id is not None) else metal.Id
            if investment_id is None:
                print(f"{ticker} ; no investment id available in API, skipping sync")
                continue

            api_existing_pricerecs: list[MinimalPriceRecord] = await api.get_sorted_pricerecs(ticker)
            latest_api_date = _coerce_to_date(api_existing_pricerecs[-1].date) if api_existing_pricerecs else None
            if latest_api_date:
                print(f"{ticker} ; API latest date: {latest_api_date}")

            new_records = price_cache.load_cached_pricerecords(
                ticker,
                investment_id,
                from_date_exclusive=latest_api_date,
            )

            await _sync_price_records_to_api(api, ticker, new_records)
    finally:
        await api.close()
