"""Shared fixtures: context defaults and the Google-Form POST intercept (AC6)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs

import pytest
from playwright.sync_api import Page, Request, Route

from w75_listing.product import BASE_URL, FORM_ACTION_GLOB

GOOGLE_HOST = "docs.google.com"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "locale": "zh-TW",
        "viewport": {"width": 1440, "height": 900},
    }


@dataclass
class Intercept:
    """Bodies the page tried to POST to the course Google Form, and every request it made to that host."""

    bodies: list[str] = field(default_factory=list)
    google_requests: list[str] = field(default_factory=list)

    def entries(self, index: int = 0) -> dict[str, str]:
        return {key: values[0] for key, values in parse_qs(self.bodies[index]).items()}

    def payload(self, index: int = 0) -> dict[str, Any]:
        return json.loads(self.entries(index)["entry.00000003"])

    def assert_clean(self) -> None:
        # AC6: exactly one submission, and every request to Google was the routed one.
        assert len(self.bodies) == 1, self.bodies
        assert len(self.google_requests) == 1, self.google_requests
        assert self.google_requests[0].endswith("/formResponse"), self.google_requests


@pytest.fixture
def intercept(page: Page) -> Intercept:
    box = Intercept()

    def fulfil(route: Route) -> None:
        box.bodies.append(route.request.post_data or "")
        route.fulfill(status=200, body="")

    def log(request: Request) -> None:
        if GOOGLE_HOST in request.url:
            box.google_requests.append(request.url)

    page.on("request", log)
    page.route(FORM_ACTION_GLOB, fulfil)
    return box
