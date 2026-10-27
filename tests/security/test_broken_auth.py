"""Broken access control and authentication (OWASP A01 / A07).

Write operations on the booking API must require a valid session token; an unauthenticated caller
must not be able to change or remove another party's record.
"""

import pytest

from config.settings import settings
from framework.api import booking_payload

pytestmark = [pytest.mark.security, pytest.mark.authz]


def _token(booker):
    return booker.create_token(settings.api_username, settings.api_password).json()["token"]


@pytest.mark.smoke
def test_delete_without_token_is_forbidden(booker):
    booking_id = booker.create_booking(booking_payload()).json()["bookingid"]
    try:
        assert booker.delete_booking(booking_id).status_code == 403
        assert booker.get_booking(booking_id).status_code == 200, "Record removed without authorisation"
    finally:
        booker.delete_booking(booking_id, token=_token(booker))


def test_update_without_token_is_forbidden(booker):
    booking_id = booker.create_booking(booking_payload()).json()["bookingid"]
    try:
        tampered = booking_payload(firstname="Mallory", totalprice=0)
        assert booker.update_booking(booking_id, tampered).status_code == 403
        assert booker.get_booking(booking_id).json()["firstname"] != "Mallory", "Record changed without authorisation"
    finally:
        booker.delete_booking(booking_id, token=_token(booker))
