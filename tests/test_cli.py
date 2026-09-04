"""The CLI dry run leaves the same proof as the suite: a decoded payload file that equals EXPECTED."""

import json
from pathlib import Path

from w75_listing.__main__ import main
from w75_listing.product import EXPECTED


def test_dry_run_writes_verified_payload(tmp_path: Path) -> None:
    assert main(["--platform", "market", "--runs-dir", str(tmp_path)]) == 0

    run_dirs = list(tmp_path.iterdir())
    assert len(run_dirs) == 1 and run_dirs[0].name.endswith("-dry")
    payload = json.loads((run_dirs[0] / "market-payload.json").read_text(encoding="utf-8"))
    assert payload["data"] == EXPECTED["market"]
    ids = (run_dirs[0] / "submission-ids.txt").read_text(encoding="utf-8")
    assert payload["submissionId"] in ids
    assert (run_dirs[0] / "market.png").exists()
