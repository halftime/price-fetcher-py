# price-fetcher-py

### Sample code for [price-web-api](https://github.com/halftime/price-web-api)

Run `python morningstarfetch.py` to sync daily closing prices for the configured
funds. The sync uses Morningstar's public `lt.morningstar.com` time-series endpoint
and does not need a chart token. Fetch failures stop the run with an error; zero
records to sync means a successful fetch found no new prices.

`MorningstarClient.fetch_price_history(...)` supplies these daily closing prices.
Prices retain the configured currencies: EUR for VWCE, IWDA and SXRS; USD for V3AA,
RBOT and VOLT. The chart methods (`fetch_chart_history` and `fetch_history`) still
provide OHLCV data and require a Morningstar chart token.
