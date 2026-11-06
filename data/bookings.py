"""Test data builders for the restful-booker API."""

import random
import string
from datetime import date, timedelta


def _suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def booking_payload(**overrides) -> dict:
    """A valid booking with unique names, so parallel runs never collide."""
    check_in = date.today() + timedelta(days=random.randint(1, 60))
    payload = {
        "firstname": f"Test{_suffix()}",
        "lastname": f"User{_suffix()}",
        "totalprice": random.randint(50, 900),
        "depositpaid": True,
        "bookingdates": {
            "checkin": check_in.isoformat(),
            "checkout": (check_in + timedelta(days=3)).isoformat(),
        },
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload
