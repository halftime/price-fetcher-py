import httpx
import pytest
from funddata import FundInfo


@pytest.fixture
def sample_fund():
    return FundInfo(
        symbol="VWCE",
        name="Vanguard FTSE All-World ETF UCITS Acc",
        morningStarId="0P0001I3S0",
        iSIN="IE00BK5BQT80",
    )


def test_addfund_returns_201_or_409(base_url, sample_fund):
    payload = {
        "symbol": sample_fund.symbol,
        "name": sample_fund.name,
        "morningStarId": sample_fund.morningStarId,
        "iSIN": sample_fund.iSIN,
    }
    response = httpx.post(f"{base_url}/addfund", json=payload)
    assert response.status_code in (201, 409), (
        f"Expected 201 or 409, got {response.status_code}: {response.text}"
    )


def test_addfund_missing_required_fields_returns_400(base_url):
    response = httpx.post(f"{base_url}/addfund", json={"symbol": "VWCE"})
    assert response.status_code == 400


def test_addfund_empty_body_returns_400(base_url):
    response = httpx.post(f"{base_url}/addfund", json={})
    assert response.status_code == 400


def test_addfund_response_contains_id_on_success(base_url, sample_fund):
    payload = {
        "symbol": sample_fund.symbol,
        "name": sample_fund.name,
        "morningStarId": sample_fund.morningStarId,
        "iSIN": sample_fund.iSIN,
    }
    response = httpx.post(f"{base_url}/addfund", json=payload)
    if response.status_code == 201:
        body = response.json()
        assert "id" in body or "Id" in body, f"Response missing id field: {body}"
