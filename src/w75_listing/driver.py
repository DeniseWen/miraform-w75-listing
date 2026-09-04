"""Playwright driver for the three sandbox listing forms.

Locators are the inputs' ``name`` attributes (unique per page except the checkbox groups),
which are also the keys the page reads back through ``FormData`` — so ``FIELDS`` and the
posted payload speak the same names.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from .product import FIELDS, SUCCESS_TEXT, FieldValue

STEP_TIMEOUT_MS = 2_000
STEP_RETRIES = 5
UPLOAD_TIMEOUT_MS = 20_000
SUBMIT_TIMEOUT_MS = 15_000
HYDRATION_TIMEOUT_MS = 90_000

# React attaches a __reactProps$<hash> expando to every element it owns once hydrated;
# before that, clicks on step buttons and the submit are inert (measured: 0.4 s to 62 s
# per fresh context on this host).
JS_FORM_HYDRATED = """() => {
  const button = document.querySelector("form button");
  return !!button && Object.keys(button).some((key) => key.startsWith("__reactProps"));
}"""

ASSET_OK_TEXT = "素材已辨識"
MARKET_ORDER_OK_TEXT = "4 張教材素材順序正確"
MARKET_SUBMIT = "確認並上架商品"

# QMarket hides inactive wizard panels with display:none, so each panel is filled only
# after its sidebar step is active.
MARKET_STEPS: dict[str, tuple[str, ...]] = {
    "基本資料": ("student", "category", "title", "brand", "model", "condition"),
    "規格與變體": ("dawnSku", "dawnPrice", "dawnStock", "mossSku", "mossPrice", "mossStock", "highlights", "origin", "warranty"),
    "物流與素材": ("weight", "length", "width", "height"),
}


def control(page: Page, name: str) -> Locator:
    # Scoped to the form: a bare [name=...] also matches <meta name="description">.
    return page.locator("form").locator(f"[name='{name}']")


def wait_hydrated(page: Page) -> None:
    page.wait_for_function(JS_FORM_HYDRATED, timeout=HYDRATION_TIMEOUT_MS)


def goto_step(page: Page, name: str) -> None:
    """Jump to a wizard step via the sidebar.

    A click that lands before React hydration is dropped silently (measured 1 in 4 with
    domcontentloaded), so the active-step ``h1`` is asserted and the click retried.
    """
    heading = page.locator("h1").first
    for attempt in range(STEP_RETRIES):
        page.get_by_role("button", name=name).click()
        try:
            expect(heading).to_have_text(name, timeout=STEP_TIMEOUT_MS)
            return
        except AssertionError:
            if attempt == STEP_RETRIES - 1:
                raise


def fill_fields(page: Page, fields: dict[str, FieldValue], names: Iterable[str] | None = None) -> None:
    for name in names if names is not None else fields:
        value = fields[name]
        if isinstance(value, bool):
            control(page, name).set_checked(value)
        elif isinstance(value, list):
            for item in value:
                page.locator("form").locator(f"[name='{name}'][value='{item}']").check()
        else:
            target = control(page, name)
            if target.evaluate("el => el.tagName") == "SELECT":
                target.select_option(label=value)
            else:
                target.fill(value)


def upload_assets(page: Page, assets: Sequence[Path]) -> None:
    page.locator("input[type=file]").set_input_files([str(path) for path in assets])
    expect(page.locator(".asset-ok")).to_have_text(ASSET_OK_TEXT, timeout=UPLOAD_TIMEOUT_MS)


def submission_id(page: Page) -> str:
    return page.locator("code").first.inner_text().strip()


def fill_market(page: Page, assets: Sequence[Path]) -> str:
    page.goto("/market", wait_until="domcontentloaded")
    wait_hydrated(page)
    fields = FIELDS["market"]
    for step, names in MARKET_STEPS.items():
        goto_step(page, step)
        fill_fields(page, fields, names)
        if step == "物流與素材":
            upload_assets(page, assets)
    goto_step(page, "檢查上架")
    expect(page.get_by_text(MARKET_ORDER_OK_TEXT)).to_be_visible()
    page.get_by_role("button", name=MARKET_SUBMIT).click()
    expect(page.get_by_text(SUCCESS_TEXT["market"])).to_be_visible(timeout=SUBMIT_TIMEOUT_MS)
    return submission_id(page)

STUDIO_SUBMIT = "儲存商品"
PROCUREMENT_SUBMIT = "送審並建立料號"


def _fill_single_page(page: Page, platform: str, assets: Sequence[Path], submit_label: str) -> str:
    # Single-page forms: every input is visible at once. Hydration is awaited first so the
    # submit click reaches React's handler instead of a native form navigation.
    page.goto(f"/{platform}", wait_until="domcontentloaded")
    wait_hydrated(page)
    fill_fields(page, FIELDS[platform])
    upload_assets(page, assets)
    page.get_by_role("button", name=submit_label).click()
    expect(page.get_by_text(SUCCESS_TEXT[platform])).to_be_visible(timeout=SUBMIT_TIMEOUT_MS)
    return submission_id(page)


def fill_studio(page: Page, assets: Sequence[Path]) -> str:
    return _fill_single_page(page, "studio", assets, STUDIO_SUBMIT)


def fill_procurement(page: Page, assets: Sequence[Path]) -> str:
    return _fill_single_page(page, "procurement", assets, PROCUREMENT_SUBMIT)


FILLERS = {"market": fill_market, "studio": fill_studio, "procurement": fill_procurement}
