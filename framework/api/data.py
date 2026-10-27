"""Test data builders. Each booking gets a unique surname so parallel runs never collide."""

from datetime import date, timedelta
from uuid import uuid4


def booking_payload(**overrides) -> dict:
    checkin = date.today() + timedelta(days=30)
    payload = {
        "firstname": "Dani",
        "lastname": f"QA-{uuid4().hex[:10]}",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": (checkin + timedelta(days=3)).isoformat(),
        },
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload
