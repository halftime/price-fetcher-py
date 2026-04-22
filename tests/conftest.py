import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "http://localhost:8080"


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=BASE_URL,
        help="Base URL for the API under test (default: http://localhost:8080)",
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")
