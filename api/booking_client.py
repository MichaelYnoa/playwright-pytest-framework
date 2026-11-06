import json

import allure
from playwright.sync_api import APIRequestContext, APIResponse


class BookingClient:
    """Thin wrapper over restful-booker endpoints; every call becomes an Allure step."""

    def __init__(self, request: APIRequestContext, token: str | None = None):
        self.request = request
        self.token = token

    def _auth_headers(self) -> dict:
        return {"Cookie": f"token={self.token}"} if self.token else {}

    def _call(self, method: str, url: str, **kwargs) -> APIResponse:
        with allure.step(f"{method.upper()} {url}"):
            response = self.request.fetch(url, method=method, **kwargs)
            allure.attach(
                response.text(),
                name=f"Response {response.status}",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response

    def create_token(self, username: str, password: str) -> APIResponse:
        return self._call("post", "/auth", data={"username": username, "password": password})

    def health(self) -> APIResponse:
        return self._call("get", "/ping")

    def list_ids(self, **filters) -> APIResponse:
        return self._call("get", "/booking", params=filters)

    def get(self, booking_id: int) -> APIResponse:
        return self._call("get", f"/booking/{booking_id}")

    def create(self, payload: dict) -> APIResponse:
        with allure.step("Request body"):
            allure.attach(json.dumps(payload, indent=2), "payload", allure.attachment_type.JSON)
        return self._call("post", "/booking", data=payload)

    def update(self, booking_id: int, payload: dict) -> APIResponse:
        return self._call(
            "put", f"/booking/{booking_id}", data=payload, headers=self._auth_headers()
        )

    def partial_update(self, booking_id: int, fields: dict) -> APIResponse:
        return self._call(
            "patch", f"/booking/{booking_id}", data=fields, headers=self._auth_headers()
        )

    def delete(self, booking_id: int) -> APIResponse:
        return self._call("delete", f"/booking/{booking_id}", headers=self._auth_headers())
