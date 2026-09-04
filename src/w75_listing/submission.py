"""Decode and verify the body the page POSTs to the course Google Form.

The site sends five url-encoded entries; ``entry.00000003`` is the JSON wrapper
``{submissionId, submittedAt, product, platform, data}`` whose ``data`` must equal
``EXPECTED[platform]``. Shared by the test fixture and the CLI so a real run leaves the
same proof as the suite.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs

from .product import EXPECTED, PLATFORM_IDS, STUDENT

ENTRY_STUDENT = "entry.00000001"
ENTRY_PLATFORM = "entry.00000002"
ENTRY_PAYLOAD = "entry.00000003"
ENTRY_ASSETS = "entry.00000004"
ENTRY_VERSION = "entry.00000005"


def decode_entries(body: str) -> dict[str, str]:
    return {key: values[0] for key, values in parse_qs(body).items()}


def decode_payload(body: str) -> dict[str, Any]:
    return json.loads(decode_entries(body)[ENTRY_PAYLOAD])


def check_submission(body: str, platform: str, submission_id: str) -> list[str]:
    """Return every way the captured body departs from what this run should have sent."""
    entries = decode_entries(body)
    payload = decode_payload(body)
    problems: list[str] = []
    if entries.get(ENTRY_STUDENT) != STUDENT:
        problems.append(f"student: sent {entries.get(ENTRY_STUDENT)!r}, expected {STUDENT!r}")
    if entries.get(ENTRY_PLATFORM) != PLATFORM_IDS[platform]:
        problems.append(f"platform: sent {entries.get(ENTRY_PLATFORM)!r}, expected {PLATFORM_IDS[platform]!r}")
    if payload.get("submissionId") != submission_id:
        problems.append(f"submissionId: payload {payload.get('submissionId')!r} != page {submission_id!r}")
    data = payload.get("data", {})
    expected = EXPECTED[platform]
    for key in sorted(set(expected) | set(data)):
        if data.get(key) != expected.get(key):
            problems.append(f"data.{key}: sent {json.dumps(data.get(key), ensure_ascii=False)[:120]} != expected {json.dumps(expected.get(key), ensure_ascii=False)[:120]}")
    return problems
