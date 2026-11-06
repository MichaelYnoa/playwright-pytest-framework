import allure
import pytest

from config.settings import settings

pytestmark = [pytest.mark.api, allure.feature("API authentication")]


@pytest.mark.smoke
def test_service_is_up(booking_api):
    assert booking_api.health().status == 201


@pytest.mark.smoke
def test_valid_credentials_return_a_token(booking_api):
    response = booking_api.create_token(settings.api_username, settings.api_password)

    assert response.status == 200
    assert response.json()["token"]


@pytest.mark.regression
def test_bad_credentials_are_rejected(booking_api):
    response = booking_api.create_token(settings.api_username, "wrong-password")

    # restful-booker answers 200 with an error body instead of 401.
    assert response.status == 200
    assert response.json() == {"reason": "Bad credentials"}
