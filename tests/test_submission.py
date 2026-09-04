"""Decoding + verification of a captured Google-Form body (shared by the tests and the CLI)."""

import json
from urllib.parse import urlencode

from w75_listing.product import EXPECTED, PLATFORM_IDS, STUDENT
from w75_listing.submission import (
    ENTRY_ASSETS,
    ENTRY_PAYLOAD,
    ENTRY_PLATFORM,
    ENTRY_STUDENT,
    ENTRY_VERSION,
    check_submission,
    decode_entries,
    decode_payload,
)

SID = "0a196429-4961-4afe-ac8e-60983fdcfc24"


def _body(platform: str = "market", **overrides: str) -> str:
    payload = {"submissionId": SID, "submittedAt": "2026-09-04T06:27:26.000Z", "product": "Miraform W75",
               "platform": PLATFORM_IDS[platform], "data": EXPECTED[platform]}
    entries = {ENTRY_STUDENT: STUDENT, ENTRY_PLATFORM: PLATFORM_IDS[platform], ENTRY_PAYLOAD: json.dumps(payload),
               ENTRY_ASSETS: "[]", ENTRY_VERSION: "1.0.0"}
    entries.update(overrides)
    return urlencode(entries)


def test_decode_round_trips_entries_and_payload() -> None:
    body = _body()
    assert decode_entries(body)[ENTRY_STUDENT] == STUDENT
    assert decode_payload(body)["data"] == EXPECTED["market"]


def test_check_submission_accepts_a_faithful_body() -> None:
    assert check_submission(_body("studio"), "studio", SID) == []


def test_check_submission_reports_each_mismatch() -> None:
    wrong_student = check_submission(_body(**{ENTRY_STUDENT: "LAB-0142"}), "market", SID)
    wrong_platform = check_submission(_body(), "studio", SID)
    wrong_id = check_submission(_body(), "market", "not-the-id")
    assert any("student" in m for m in wrong_student)
    assert any("platform" in m for m in wrong_platform)
    assert any("submissionId" in m for m in wrong_id)
