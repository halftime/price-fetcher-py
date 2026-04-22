import httpx
import pytest
from fund import PreciousMetal
from pricerecord import MinimalPriceRecord

@pytest.fixture
def sample_metal():
    return PreciousMetal(symbol="XAU", name="Gold")


@pytest.fixture
def sample_price_record(sample_metal):
    return {
        "symbol": sample_metal.symbol,  # Should be set to a valid ID in your test DB
        #"investmentId": 1,  # Assuming this ID exists for the test
        "price": 2000.0,
        "date": "2020-01-01"
    }

def test_add_price_record(base_url, sample_price_record):
    response = httpx.post(f"{base_url}/addpricerecord", json=sample_price_record)
    assert response.status_code in (201, 409), f"Unexpected status: {response.status_code} {response.text}"


def test_add_duplicate_price_record(base_url, sample_price_record):
    # Add once
    httpx.post(f"{base_url}/addpricerecord", json=sample_price_record)
    # Add duplicate
    response = httpx.post(f"{base_url}/addpricerecord", json=sample_price_record)
    assert response.status_code == 409, f"Expected 409 for duplicate, got {response.status_code}"


def test_update_price_record(base_url, sample_price_record):
    # Add record
    httpx.post(f"{base_url}/addpricerecord", json=sample_price_record)
    # Change price
    updated = dict(sample_price_record)
    updated["price"] = 2100.0

    response = httpx.post(f"{base_url}/addpricerecord", json=updated) # not using put
    assert response.status_code in (200, 201, 409), f"Unexpected status: {response.status_code} {response.text}"

def get_updated_pricerecord(base_url, sample_price_record):
    #checking made record
    get_resp = httpx.get(f"{base_url}/pricerecord/{sample_price_record['symbol']}/{sample_price_record['date']}")
    assert get_resp.status_code == 200, f"Status code not 200: {get_resp.status_code} {get_resp.text}"
    data = get_resp.json()
    assert data["price"] == 2100.0, f"Price not updated: {data}"
