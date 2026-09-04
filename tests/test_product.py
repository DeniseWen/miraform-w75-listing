"""AC2: data guards over EXPECTED — no fabricated GTIN, clean highlights, consistent SKU/price/stock."""

from w75_listing.product import EXPECTED, STUDENT

SKUS = ("MFW75-WN-DN", "MFW75-WN-MS")
STOCKS = ("36", "24")


def test_student_id() -> None:
    assert STUDENT == "MFW75-PRACTICE"


def test_gtin_is_not_fabricated() -> None:
    assert EXPECTED["procurement"]["identity"]["gtin"] == "未申請"


def test_market_highlights_contain_no_price_shipping_or_certification_claims() -> None:
    highlights = EXPECTED["market"]["highlights"]
    assert len(highlights.splitlines()) == 5
    for banned in ("NT$", "免運", "認證"):
        assert banned not in highlights


def test_prices_are_4680_everywhere() -> None:
    assert [v["price"] for v in EXPECTED["market"]["variants"]] == ["4680", "4680"]
    assert EXPECTED["studio"]["pricing"]["price"] == "4680"


def test_skus_and_stocks_are_consistent_across_platforms() -> None:
    assert tuple(v["sku"] for v in EXPECTED["market"]["variants"]) == SKUS
    assert tuple(v["sku"] for v in EXPECTED["studio"]["variants"]) == SKUS
    assert tuple(v["stock"] for v in EXPECTED["market"]["variants"]) == STOCKS
    assert tuple(v["stock"] for v in EXPECTED["studio"]["variants"]) == STOCKS
