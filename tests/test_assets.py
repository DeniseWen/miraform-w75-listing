"""AC1: the vendored PNGs are byte-identical to the course pack, in manifest order."""

import csv
import hashlib

from w75_listing.product import ASSET_ORDER, ASSETS_DIR


def _manifest() -> list[dict[str, str]]:
    with open(ASSETS_DIR / "asset-manifest.csv", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return sorted(rows, key=lambda r: int(r["order"]))


def test_every_png_matches_manifest_sha256() -> None:
    rows = _manifest()
    assert len(rows) == 4
    for row in rows:
        digest = hashlib.sha256((ASSETS_DIR / row["filename"]).read_bytes()).hexdigest()
        assert digest == row["sha256"], row["filename"]


def test_asset_order_follows_manifest() -> None:
    assert ASSET_ORDER == tuple(row["filename"] for row in _manifest())
    assert [int(r["order"]) for r in _manifest()] == [1, 2, 3, 4]
