import allure
import pytest

from api.schemas import AuthError, Booking, BookingRef, CreatedBooking, Token, validate
from config.settings import settings
from data.bookings import booking_payload

pytestmark = [pytest.mark.api, allure.feature("API contracts")]


@pytest.mark.smoke
def test_auth_token_contract(booking_api):
    response = booking_api.create_token(settings.api_username, settings.api_password)

    assert response.status == 200
    validate(response, Token)


@pytest.mark.regression
def test_bad_credentials_contract(booking_api):
    response = booking_api.create_token(settings.api_username, "wrong-password")

    validate(response, AuthError)


@pytest.mark.smoke
def test_create_booking_contract(authed_booking_api):
    payload = booking_payload()

    response = authed_booking_api.create(payload)

    assert response.status == 200
    created = validate(response, CreatedBooking)
    authed_booking_api.delete(created.bookingid)
    assert created.booking.model_dump(mode="json") == payload


@pytest.mark.regression
def test_get_booking_contract(booking_api, created_booking):
    booking_id, payload = created_booking

    response = booking_api.get(booking_id)

    assert response.status == 200
    booking = validate(response, Booking)
    assert booking.model_dump(mode="json") == payload


@pytest.mark.regression
def test_optional_field_is_omitted_when_not_sent(authed_booking_api):
    payload = booking_payload()
    del payload["additionalneeds"]

    response = authed_booking_api.create(payload)

    created = validate(response, CreatedBooking)
    authed_booking_api.delete(created.bookingid)
    assert "additionalneeds" not in response.json()["booking"]


@pytest.mark.regression
def test_list_bookings_contract(booking_api, created_booking):
    booking_id, payload = created_booking

    response = booking_api.list_ids(firstname=payload["firstname"], lastname=payload["lastname"])

    assert response.status == 200
    refs = validate(response, list[BookingRef])
    assert [ref.bookingid for ref in refs] == [booking_id]
