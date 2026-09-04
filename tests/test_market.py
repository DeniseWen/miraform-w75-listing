"""AC3 (+AC6): QMarket wizard fills, recognises the 4 PNGs in order, submits, and posts EXPECTED['market']."""

import re

from playwright.sync_api import Page, expect

from w75_listing.driver import fill_market
from w75_listing.product import ASSET_PATHS, EXPECTED, PLATFORM_IDS, STUDENT, SUCCESS_TEXT

from conftest import Intercept

UUID4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_market_listing_submits_expected_payload(page: Page, intercept: Intercept) -> None:
    submission_id = fill_market(page, ASSET_PATHS)

    expect(page.get_by_text(SUCCESS_TEXT["market"])).to_be_visible()
    assert UUID4.match(submission_id), submission_id

    entries = intercept.entries()
    assert entries["entry.00000001"] == STUDENT
    assert entries["entry.00000002"] == PLATFORM_IDS["market"]
    assert intercept.payload()["data"] == EXPECTED["market"]
    intercept.assert_clean()
