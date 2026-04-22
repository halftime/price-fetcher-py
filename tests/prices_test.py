# File renamed to test_prices.py
import httpx
import pytest


def test_get_prices_vwce_returns_200(base_url):
    response = httpx.get(f"{base_url}/prices/VWCE")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )


def test_get_prices_vwce_returns_list(base_url):
    response = httpx.get(f"{base_url}/prices/VWCE")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list), f"Expected a list, got: {type(body)}"


def test_get_prices_vwce_records_have_required_fields(base_url):
    response = httpx.get(f"{base_url}/prices/VWCE")
    assert response.status_code == 200
    records = response.json()
    for record in records:
        assert "date" in record, f"Record missing 'date': {record}"
        assert "symbol" in record, f"Record missing 'symbol': {record}"
        assert "price" in record, f"Record missing 'price': {record}"


def test_get_prices_unknown_ticker_returns_404(base_url):
    response = httpx.get(f"{base_url}/prices/UNKNOWN_TICKER_XYZ")
    assert response.status_code == 404, (
        f"Expected 404, got {response.status_code}: {response.text}"
    )
