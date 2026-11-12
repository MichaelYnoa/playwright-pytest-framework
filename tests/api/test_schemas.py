"""Offline checks that the contracts are strict enough to catch real API drift."""

import json

import allure
import pytest
from pydantic import ValidationError

from api.schemas import Booking
from data.bookings import booking_payload

pytestmark = [pytest.mark.api, allure.feature("API contracts")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"totalprice": "120"}, id="price-as-string"),
        pytest.param({"depositpaid": "true"}, id="bool-as-string"),
        pytest.param({"firstname": ""}, id="empty-name"),
        pytest.param({"bookingdates": {"checkin": "2026-12-01"}}, id="missing-checkout"),
        pytest.param(
            {"bookingdates": {"checkin": "01/12/2026", "checkout": "2026-12-04"}}, id="non-iso-date"
        ),
        pytest.param({"currency": "USD"}, id="unexpected-field"),
    ],
)
def test_booking_schema_rejects_drift(change):
    body = {**booking_payload(), **change}

    with pytest.raises(ValidationError):
        Booking.model_validate_json(json.dumps(body))
