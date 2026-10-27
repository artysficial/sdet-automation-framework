import pytest

from config.settings import settings
from framework.api import BookerClient, booking_payload


@pytest.fixture(scope="session")
def api() -> BookerClient:
    return BookerClient(settings.api_base_url, timeout=settings.api_timeout)


@pytest.fixture(scope="session")
def token(api) -> str:
    response = api.create_token(settings.api_username, settings.api_password)
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def booking(api, token):
    """A fresh booking for one test, removed afterwards so the shared demo service stays clean."""
    payload = booking_payload()
    response = api.create_booking(payload)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield booking_id, payload
    api.delete_booking(booking_id, token=token)
