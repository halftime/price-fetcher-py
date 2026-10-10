import asyncio
from datetime import date

import httpx
import pytest

from morningstarclient import MorningstarClient, MorningstarFetchError


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


def test_collect_maas_token_reads_maas_token_and_caches_across_securities():
    captured = []

    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            captured.append(url)
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                text='payload:{maasToken:"header.payload.signature"}',
            )

        client._get_with_retry = fake_get
        try:
            first_token = await client.collect_maas_token("F00000XPTP")
            second_token = await client.collect_maas_token("0P0001D6YY")
            return first_token, second_token
        finally:
            await client.close()

    first_token, second_token = asyncio.run(run_test())

    assert first_token == "header.payload.signature"
    assert second_token == first_token
    assert captured == [MorningstarClient.CHART_TOKEN_PAGE_URL]


def test_collect_maas_token_prefers_maas_token_over_unrelated_token():
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                text='analytics:{token:"unrelated-token"},payload:{maasToken:"chart-token"}',
            )

        client._get_with_retry = fake_get
        try:
            return await client.collect_maas_token("F00000XPTP")
        finally:
            await client.close()

    assert asyncio.run(run_test()) == "chart-token"


@pytest.mark.parametrize("token_key", ["maasToken", "token"])
@pytest.mark.parametrize(
    "token_property",
    [
        '{key}:"header.payload.signature"',
        '"{key}":"header.payload.signature"',
        '"{key}" \n : \t "header.payload.signature"',
        "'{key}' : 'header.payload.signature'",
        "{key} : 'header.payload.signature'",
    ],
)
def test_collect_maas_token_supports_javascript_and_json_properties(token_key, token_property):
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                text="payload:{" + token_property.format(key=token_key) + "}",
            )

        client._get_with_retry = fake_get
        try:
            return await client.collect_maas_token("F00000XPTP")
        finally:
            await client.close()

    assert asyncio.run(run_test()) == "header.payload.signature"


@pytest.mark.parametrize(
    "invalid_page",
    [
        "<html><body>Token unavailable</body></html>",
        'payload:{maasToken:"header.payload.signature',
        'payload:{token:"header.payload.signature',
        'payload:{maasToken:""}',
        'payload:{token:""}',
    ],
)
def test_collect_maas_token_rejects_missing_truncated_or_empty_token_without_caching(invalid_page):
    captured = []

    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            captured.append(url)
            page = invalid_page if len(captured) == 1 else 'payload:{maasToken:"valid-token"}'
            return httpx.Response(200, request=httpx.Request("GET", url), text=page)

        client._get_with_retry = fake_get
        try:
            with pytest.raises(Exception, match="chart token was not found"):
                await client.collect_maas_token("F00000XPTP")
            assert client._maas_token is None
            return await client.collect_maas_token("F00000XPTP")
        finally:
            await client.close()

    assert asyncio.run(run_test()) == "valid-token"
    assert len(captured) == 2


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


@pytest.mark.parametrize(
    ("security_id", "currency"),
    [
        ("0P0001I3S0", "EUR"),
        ("F000016OZH", "USD"),
        ("0P0000MLIH", "EUR"),
        ("0P0001D6YY", "EUR"),
        ("F000014VZD", "USD"),
        ("F00000XPTP", "USD"),
    ],
)
def test_price_history_fetches_daily_prices_without_chart_authentication(security_id, currency):
    captured = []

    async def run_test():
        client = MorningstarClient()

        async def unexpected_chart_request(*args, **kwargs):
            pytest.fail("Price history must not request a chart token or chart history")

        async def fake_get(url, headers, params=None):
            captured.append((url, headers, params))
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                json={
                    "TimeSeries": {
                        "Security": [{"HistoryDetail": [{"EndDate": "2026-10-01", "Value": "31.4"}]}]
                    }
                },
            )

        client.collect_maas_token = unexpected_chart_request
        client.fetch_chart_history = unexpected_chart_request
        client._get_with_retry = fake_get
        try:
            return await client.fetch_price_history(
                security_id,
                start_date=date(2026, 9, 30),
                end_date=date(2026, 10, 10),
            )
        finally:
            await client.close()

    series = asyncio.run(run_test())

    assert len(captured) == 1
    url, headers, params = captured[0]
    assert url == "https://lt.morningstar.com/api/rest.svc/timeseries_price/t92wz0sj7c"
    assert headers["Referer"] == "https://lt.morningstar.com/"
    assert "Authorization" not in headers
    assert params == {
        "currencyId": currency,
        "idtype": "Morningstar",
        "frequency": "daily",
        "outputType": "JSON",
        "priceType": "PRICE",
        "startDate": "2026-09-30",
        "endDate": "2026-10-10",
        "id": f"{security_id}]2]0]FOEUR$$ALL",
    }
    assert [(item.date, item.close) for item in series] == [(date(2026, 10, 1), 31.4)]


def test_price_history_defaults_to_today_and_returns_sorted_close_records():
    captured = []

    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            captured.append(params)
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                json={
                    "TimeSeries": {
                        "Security": [{"HistoryDetail": [
                            {"EndDate": "2026-10-02", "Value": "33.2"},
                            {"EndDate": "2026-10-01", "Value": "31.4"},
                        ]}]
                    }
                },
            )

        client._get_with_retry = fake_get
        try:
            return await client.fetch_price_history("F00000XPTP", start_date=date(2026, 9, 30))
        finally:
            await client.close()

    series = asyncio.run(run_test())

    assert captured[0]["endDate"] == date.today().isoformat()
    assert [(item.date, item.close) for item in series] == [
        (date(2026, 10, 1), 31.4),
        (date(2026, 10, 2), 33.2),
    ]
    for item in series:
        assert item.nav is None
        assert item.open is None
        assert item.high is None
        assert item.low is None
        assert item.volume is None


@pytest.mark.parametrize(
    "security",
    [
        {"Id": "F00000XPTP", "HistoryDetail": []},
        {"Id": "F00000XPTP"},
    ],
)
def test_price_history_successful_empty_response_returns_no_records(security):
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                json={"TimeSeries": {"Security": [security]}},
            )

        client._get_with_retry = fake_get
        try:
            return await client.fetch_price_history("F00000XPTP", start_date=date(2026, 8, 1))
        finally:
            await client.close()

    assert asyncio.run(run_test()) == []


@pytest.mark.parametrize(
    ("status_code", "body"),
    [
        (503, "Service unavailable"),
        (200, "<html>Unexpected source response</html>"),
        (200, '{"error":"No price history available"}'),
        (200, '{"TimeSeries":{"Security":{}}}'),
        (200, '{"TimeSeries":{"Security":[{"HistoryDetail":{}}]}}'),
    ],
)
def test_price_history_source_failures_raise_instead_of_returning_no_records(status_code, body):
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return httpx.Response(status_code, request=httpx.Request("GET", url), text=body)

        client._get_with_retry = fake_get
        try:
            with pytest.raises(MorningstarFetchError):
                await client.fetch_price_history("F00000XPTP", start_date=date(2026, 8, 1))
        finally:
            await client.close()

    asyncio.run(run_test())


def test_price_history_request_failure_raises_instead_of_returning_no_records():
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return None

        client._get_with_retry = fake_get
        try:
            with pytest.raises(MorningstarFetchError):
                await client.fetch_price_history("F00000XPTP", start_date=date(2026, 8, 1))
        finally:
            await client.close()

    asyncio.run(run_test())


@pytest.mark.parametrize(
    "invalid_record",
    [
        {"EndDate": "2026-13-01", "Value": "31.4"},
        {"EndDate": 20260831, "Value": "31.4"},
        {"EndDate": "2026-08-31", "Value": "not-a-price"},
        {"EndDate": "2026-08-31", "Value": {"amount": 31.4}},
    ],
)
def test_price_history_invalid_record_raises_instead_of_returning_partial_history(invalid_record):
    async def run_test():
        client = MorningstarClient()

        async def fake_get(url, headers, params=None):
            return httpx.Response(
                200,
                request=httpx.Request("GET", url),
                json={
                    "TimeSeries": {"Security": [{"HistoryDetail": [
                        {"EndDate": "2026-07-31", "Value": "30.1"},
                        invalid_record,
                    ]}]}
                },
            )

        client._get_with_retry = fake_get
        try:
            with pytest.raises(MorningstarFetchError, match="F00000XPTP: invalid date or price value"):
                await client.fetch_price_history("F00000XPTP", start_date=date(2026, 7, 1))
        finally:
            await client.close()

    asyncio.run(run_test())
