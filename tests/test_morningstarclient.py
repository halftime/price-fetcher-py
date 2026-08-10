import asyncio
from datetime import date

import httpx

from morningstarclient import MorningstarClient


def test_collect_maas_token_uses_current_token_page_and_caches_token():
    captured = []

    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            captured.append((url, headers, params))
            request = httpx.Request("GET", url)
            return httpx.Response(
                200,
                request=request,
                text='payload:{isLocked:false,token:"header.payload.signature"}',
            )

        client._get_with_retry = fake_get
        try:
            first_token = await client.collect_maas_token("0P0001D6YY")
            second_token = await client.collect_maas_token("another-id")
            return first_token, second_token
        finally:
            await client.close()

    first_token, second_token = asyncio.run(run_test())

    assert first_token == "header.payload.signature"
    assert second_token == first_token
    assert len(captured) == 1
    assert captured[0][0] == MorningstarClient.CHART_TOKEN_PAGE_URL
    assert captured[0][1]["Accept"].startswith("text/html")


def test_chart_history_uses_morningstar_id_and_today():
    captured = {}

    async def run_test():
        client = MorningstarClient()

        async def fake_collect_maas_token(morningstar_id):
            assert morningstar_id == "0P0001D6YY"
            return "test-token"

        async def fake_get(url, headers, params=None):
            captured.update(url=url, headers=headers, params=params)
            request = httpx.Request("GET", url)
            return httpx.Response(
                200,
                request=request,
                json=[
                    {
                        "series": [
                            {
                                "date": "2026-08-07",
                                "open": 31.1,
                                "high": 31.5,
                                "low": 30.9,
                                "close": 31.4,
                                "volume": 1234,
                                "nav": 31.3,
                                "totalReturn": 44.2,
                                "previousClose": 31.0,
                            }
                        ]
                    }
                ],
            )

        client.collect_maas_token = fake_collect_maas_token
        client._get_with_retry = fake_get
        try:
            return await client.fetch_history(
                "0P0001D6YY",
                start_date=date(1900, 1, 1),
            )
        finally:
            await client.close()

    series = asyncio.run(run_test())

    assert captured["url"] == MorningstarClient.CHART_SERVICE_URL
    assert captured["params"] == {
        "query": "0P0001D6YY:open,high,low,close,volume,previousClose",
        "frequency": "m",
        "startDate": "1900-01-01",
        "endDate": date.today().isoformat(),
        "trackMarketData": "3.6.5",
        "instid": "DOTCOM",
    }
    assert captured["headers"]["Authorization"] == "Bearer test-token"
    assert len(series) == 1
    assert series[0].date == date(2026, 8, 7)
    assert series[0].close == 31.4
