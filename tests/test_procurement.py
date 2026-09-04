"""AC5 (+AC6): SupplyDesk sheet (sections A–E, 6 BOM rows, 4 declarations) submits EXPECTED['procurement']."""

from playwright.sync_api import Page, expect

from w75_listing.driver import fill_procurement
from w75_listing.product import ASSET_PATHS, EXPECTED, PLATFORM_IDS, STUDENT, SUCCESS_TEXT

from conftest import Intercept
from test_market import UUID4


def test_procurement_sheet_submits_expected_payload(page: Page, intercept: Intercept) -> None:
    submission_id = fill_procurement(page, ASSET_PATHS)

    expect(page.get_by_text(SUCCESS_TEXT["procurement"])).to_be_visible()
    assert UUID4.match(submission_id), submission_id

    entries = intercept.entries()
    assert entries["entry.00000001"] == STUDENT
    assert entries["entry.00000002"] == PLATFORM_IDS["procurement"]
    data = intercept.payload()["data"]
    assert len(data["declarations"]) == 4
    assert data["identity"]["gtin"] == "未申請"
    assert len(data["bom"]) == 6
    assert data == EXPECTED["procurement"]
    intercept.assert_clean()
