import httpx
import pytest
from fund import PreciousMetal


@pytest.fixture
def sample_metal():
    return PreciousMetal(
        symbol="XAU",
        name="Gold",
    )


def test_addmetal_returns_201_or_409(base_url, sample_metal):
    payload = {
        "symbol": sample_metal.symbol,
        "name": sample_metal.name,
    }
    response = httpx.post(f"{base_url}/addmetal", json=payload)
    assert response.status_code in (201, 409), (
        f"Expected 201 or 409, got {response.status_code}: {response.text}"
    )


def test_addmetal_missing_required_fields_returns_400(base_url):
    response = httpx.post(f"{base_url}/addmetal", json={"symbol": "XAU"})
    assert response.status_code == 400


def test_addmetal_empty_body_returns_400(base_url):
    response = httpx.post(f"{base_url}/addmetal", json={})
    assert response.status_code == 400


def test_addmetal_response_contains_id_on_success(base_url, sample_metal):
    payload = {
        "symbol": sample_metal.symbol,
        "name": sample_metal.name,
    }
    response = httpx.post(f"{base_url}/addmetal", json=payload)
    if response.status_code == 201:
        body = response.json()
        assert "id" in body or "Id" in body, f"Response missing id field: {body}"


def test_addmetal_invalid_ticker_returns_400(base_url):
    payload = {"symbol": "", "name": "Gold"}
    response = httpx.post(f"{base_url}/addmetal", json=payload)
    assert response.status_code == 400
