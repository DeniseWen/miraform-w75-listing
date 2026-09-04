"""AC4 (+AC6): Store Studio single-page form submits EXPECTED['studio']."""

from playwright.sync_api import Page, expect

from w75_listing.driver import fill_studio
from w75_listing.product import ASSET_PATHS, EXPECTED, PLATFORM_IDS, STUDENT, SUCCESS_TEXT

from conftest import Intercept
from test_market import UUID4


def test_studio_listing_submits_expected_payload(page: Page, intercept: Intercept) -> None:
    submission_id = fill_studio(page, ASSET_PATHS)

    expect(page.get_by_text(SUCCESS_TEXT["studio"])).to_be_visible()
    assert UUID4.match(submission_id), submission_id

    entries = intercept.entries()
    assert entries["entry.00000001"] == STUDENT
    assert entries["entry.00000002"] == PLATFORM_IDS["studio"]
    data = intercept.payload()["data"]
    assert data["status"] == "啟用"
    assert data["salesChannels"] == ["網路商店"]
    assert data["pricing"]["taxable"] is True
    assert data == EXPECTED["studio"]
    intercept.assert_clean()
