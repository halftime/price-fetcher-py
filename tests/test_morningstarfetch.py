import asyncio
from datetime import date
from types import SimpleNamespace

import httpx
import pytest

import morningstarfetch
from morningstarclient import MorningstarFetchError
from pricerecord import MinimalPriceRecord
from seriesdata import MorningStarSeries


@pytest.fixture
def fake_sync_clients(monkeypatch):
    def configure(existing_records, source_records=(), fetch_error=None):
        fund = SimpleNamespace(symbol="RBOT", morningStarId="F00000XPTP")
        state = SimpleNamespace(
            fetch_calls=[],
            funds_added=[],
            requested_symbols=[],
            written_records=[],
            closed_clients=[],
        )

        class FakeMorningstarClient:
            async def fetch_price_history(self, security_id, *, start_date):
                state.fetch_calls.append((security_id, start_date))
                if fetch_error is not None:
                    raise fetch_error
                return source_records

            async def fetch_history(self, *args, **kwargs):
                raise AssertionError("Unattended sync must use public closing prices")

            async def close(self):
                state.closed_clients.append("morningstar")

        class FakeMyWebApi:
            async def add_fund(self, value):
                state.funds_added.append(value)

            async def get_sorted_pricerecs(self, symbol):
                state.requested_symbols.append(symbol)
                return existing_records

            async def add_price_record(self, record):
                state.written_records.append(record)
                return httpx.Response(201)

            async def close(self):
                state.closed_clients.append("api")

        monkeypatch.setattr(morningstarfetch, "MorningstarClient", FakeMorningstarClient)
        monkeypatch.setattr(morningstarfetch, "MyWebApi", FakeMyWebApi)
        monkeypatch.setattr(morningstarfetch, "UCITS_FUNDS", [fund])
        state.fund = fund
        return state

    return configure


@pytest.mark.parametrize(
    "latest_stored_date",
    [date(2026, 9, 30), "2026-09-30", "2026-09-30T00:00:00Z"],
)
def test_unattended_sync_fetches_from_latest_date_and_writes_only_new_daily_closes(
    fake_sync_clients, capsys, latest_stored_date
):
    state = fake_sync_clients(
        existing_records=[
            MinimalPriceRecord("RBOT", 9.0, date(2026, 9, 29)),
            MinimalPriceRecord("RBOT", 10.0, latest_stored_date),
        ],
        source_records=[
            MorningStarSeries(date=date(2026, 9, 29), close=9.0, nav=109.0),
            MorningStarSeries(date=date(2026, 9, 30), close=10.0, nav=110.0),
            MorningStarSeries(date=date(2026, 10, 1), close=11.0, nav=111.0),
            MorningStarSeries(date=date(2026, 10, 2), close=12.0, nav=113.0),
            MorningStarSeries(date=date(2026, 10, 3), close=None, nav=112.0),
        ],
    )

    asyncio.run(morningstarfetch.morningstarasync())

    assert state.fetch_calls == [("F00000XPTP", date(2026, 9, 30))]
    assert state.funds_added == [state.fund]
    assert state.requested_symbols == ["RBOT"]
    assert state.written_records == [
        MinimalPriceRecord("RBOT", 11.0, date(2026, 10, 1)),
        MinimalPriceRecord("RBOT", 12.0, date(2026, 10, 2)),
    ]
    assert state.closed_clients == ["api", "morningstar"]
    assert "RBOT ; price records to sync: 2" in capsys.readouterr().out


def test_unattended_sync_fetches_full_history_when_api_has_no_records(
    fake_sync_clients,
):
    state = fake_sync_clients(
        existing_records=[],
        source_records=[
            MorningStarSeries(date=date(2026, 7, 31), close=10.0, nav=110.0)
        ],
    )

    asyncio.run(morningstarfetch.morningstarasync())

    assert state.fetch_calls == [("F00000XPTP", date(1900, 1, 1))]
    assert state.written_records == [
        MinimalPriceRecord("RBOT", 10.0, date(2026, 7, 31))
    ]
    assert state.closed_clients == ["api", "morningstar"]


def test_unattended_sync_propagates_fetch_failure_without_reporting_empty_sync(
    fake_sync_clients, capsys
):
    failure = MorningstarFetchError("Public closing-price endpoint is unavailable")
    state = fake_sync_clients(
        existing_records=[
            MinimalPriceRecord("RBOT", 10.0, date(2026, 7, 31))
        ],
        fetch_error=failure,
    )

    with pytest.raises(MorningstarFetchError) as raised:
        asyncio.run(morningstarfetch.morningstarasync())

    assert raised.value is failure
    assert state.fetch_calls == [("F00000XPTP", date(2026, 7, 31))]
    assert state.written_records == []
    assert state.closed_clients == ["api", "morningstar"]
    assert "price records to sync:" not in capsys.readouterr().out
