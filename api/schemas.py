"""Response contracts for restful-booker, enforced with strict pydantic models.

Strict mode means no type coercion ("120" is not an int) and `extra="forbid"`
means an unexpected field is a contract change, not something to ignore.
"""

import json
from datetime import date
from typing import TypeVar, get_origin

import allure
from playwright.sync_api import APIResponse
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError


class Contract(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class BookingDates(Contract):
    checkin: date
    checkout: date


class Booking(Contract):
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)
    totalprice: int = Field(ge=0)
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None  # optional: omitted when not sent


class CreatedBooking(Contract):
    bookingid: int = Field(gt=0)
    booking: Booking


class BookingRef(Contract):
    bookingid: int = Field(gt=0)


class Token(Contract):
    token: str = Field(min_length=1)


class AuthError(Contract):
    reason: str


T = TypeVar("T")


def _name(schema) -> str:
    # list[BookingRef] -> "list[BookingRef]", Booking -> "Booking"
    return str(schema).replace(f"{__name__}.", "") if get_origin(schema) else schema.__name__


def validate(response: APIResponse, schema: type[T]) -> T:
    """Parse the response body against `schema`, or fail with every mismatch listed."""
    with allure.step(f"Validate response against {_name(schema)}"):
        try:
            return TypeAdapter(schema).validate_json(response.body())
        except ValidationError as error:
            allure.attach(
                json.dumps(error.errors(include_url=False), indent=2, default=str),
                name="contract violations",
                attachment_type=allure.attachment_type.JSON,
            )
            raise AssertionError(f"Response does not match {_name(schema)}:\n{error}") from None
