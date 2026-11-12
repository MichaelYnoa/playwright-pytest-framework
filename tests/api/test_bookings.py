import allure
import pytest

from data.bookings import booking_payload

pytestmark = [pytest.mark.api, allure.feature("Bookings API")]


@pytest.mark.smoke
@allure.severity(allure.severity_level.CRITICAL)
def test_create_booking_returns_what_was_sent(authed_booking_api):
    payload = booking_payload()

    response = authed_booking_api.create(payload)

    assert response.status == 200
    body = response.json()
    authed_booking_api.delete(body["bookingid"])
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload


@pytest.mark.regression
def test_filter_bookings_by_name(booking_api, created_booking):
    booking_id, payload = created_booking

    response = booking_api.list_ids(firstname=payload["firstname"], lastname=payload["lastname"])

    assert response.status == 200
    assert {"bookingid": booking_id} in response.json()


@pytest.mark.regression
def test_full_update(authed_booking_api, created_booking):
    booking_id, _ = created_booking
    new_payload = booking_payload(totalprice=999, depositpaid=False)

    response = authed_booking_api.update(booking_id, new_payload)

    assert response.status == 200
    assert authed_booking_api.get(booking_id).json() == new_payload


@pytest.mark.regression
def test_partial_update_changes_only_given_fields(authed_booking_api, created_booking):
    booking_id, payload = created_booking

    response = authed_booking_api.partial_update(booking_id, {"additionalneeds": "Late checkout"})

    assert response.status == 200
    assert authed_booking_api.get(booking_id).json() == {
        **payload,
        "additionalneeds": "Late checkout",
    }


@pytest.mark.regression
def test_delete_booking(authed_booking_api, created_booking):
    booking_id, _ = created_booking

    response = authed_booking_api.delete(booking_id)

    # restful-booker returns 201 Created for a successful DELETE.
    assert response.status == 201
    assert authed_booking_api.get(booking_id).status == 404


@pytest.mark.regression
@pytest.mark.parametrize("method", ["update", "partial_update", "delete"])
def test_write_operations_require_auth(booking_api, created_booking, method):
    booking_id, payload = created_booking
    args = {"update": (payload,), "partial_update": ({"firstname": "Hacker"},), "delete": ()}

    response = getattr(booking_api, method)(booking_id, *args[method])

    assert response.status == 403
    assert booking_api.get(booking_id).json() == payload


@pytest.mark.regression
def test_unknown_booking_returns_404(booking_api):
    assert booking_api.get(999_999_999).status == 404
