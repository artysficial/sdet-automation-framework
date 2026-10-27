"""Booking API: lifecycle, authorisation, contract and error handling.

Plain pytest rather than BDD: these checks are technical contracts, not stakeholder-facing behaviour.
"""

import pytest

from config.settings import settings
from framework.api import booking_payload
from framework.schemas import assert_matches_schema


@pytest.mark.smoke
def test_service_health_check(api):
    # restful-booker documents 201 Created for its health check
    assert api.ping().status_code == 201


@pytest.mark.smoke
@pytest.mark.contract
def test_create_booking_returns_id_and_echoes_payload(api, token):
    payload = booking_payload()
    response = api.create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload
    assert_matches_schema(body["booking"], "booking")
    api.delete_booking(body["bookingid"], token=token)


@pytest.mark.contract
@pytest.mark.regression
def test_get_booking_matches_created_record(api, booking):
    booking_id, payload = booking
    response = api.get_booking(booking_id)

    assert response.status_code == 200
    assert response.json() == payload
    assert_matches_schema(response.json(), "booking")


@pytest.mark.regression
def test_search_by_name_finds_booking(api, booking):
    booking_id, payload = booking
    response = api.find_bookings(firstname=payload["firstname"], lastname=payload["lastname"])

    assert response.status_code == 200
    assert {"bookingid": booking_id} in response.json()


@pytest.mark.regression
def test_full_update_with_token(api, token, booking):
    booking_id, _ = booking
    updated = booking_payload(firstname="Rahmadani", totalprice=275, depositpaid=False)
    response = api.update_booking(booking_id, updated, token=token)

    assert response.status_code == 200
    assert response.json() == updated
    assert api.get_booking(booking_id).json() == updated


@pytest.mark.regression
def test_partial_update_changes_only_given_fields(api, token, booking):
    booking_id, original = booking
    response = api.partial_update_booking(booking_id, {"additionalneeds": "Late checkout"}, token=token)

    assert response.status_code == 200
    assert response.json() == {**original, "additionalneeds": "Late checkout"}


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.parametrize("method", ["update", "partial_update", "delete"])
def test_write_operations_require_authorisation(api, booking, method):
    booking_id, payload = booking
    calls = {
        "update": lambda: api.update_booking(booking_id, payload),
        "partial_update": lambda: api.partial_update_booking(booking_id, {"totalprice": 1}),
        "delete": lambda: api.delete_booking(booking_id),
    }

    assert calls[method]().status_code == 403
    assert api.get_booking(booking_id).json() == payload, "Record changed without authorisation"


@pytest.mark.regression
def test_deleted_booking_is_no_longer_found(api, token):
    booking_id = api.create_booking(booking_payload()).json()["bookingid"]

    # restful-booker documents 201 Created for a successful delete
    assert api.delete_booking(booking_id, token=token).status_code == 201
    assert api.get_booking(booking_id).status_code == 404


@pytest.mark.negative
@pytest.mark.regression
def test_unknown_booking_returns_404(api):
    assert api.get_booking(999_999_999).status_code == 404


@pytest.mark.negative
@pytest.mark.known_defect
@pytest.mark.xfail(reason="DEF-002: missing required field returns 500 instead of 400", strict=True)
def test_create_booking_missing_required_field_is_rejected_as_client_error(api):
    payload = booking_payload()
    del payload["firstname"]

    assert api.create_booking(payload).status_code == 400


@pytest.mark.negative
@pytest.mark.known_defect
@pytest.mark.xfail(reason="DEF-003: invalid credentials return 200 instead of 401", strict=True)
def test_invalid_credentials_are_rejected_with_401(api):
    response = api.create_token(settings.api_username, "not-the-password")

    assert "token" not in response.json(), "A token was issued for invalid credentials"
    assert response.status_code == 401
