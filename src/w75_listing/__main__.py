"""Run the three listings end to end.

Default is a dry run: the course Google-Form POST is intercepted so nothing is recorded.
``--submit`` lets the POST through — a real submission, to be run once on explicit go.
Retry rule: re-run only the failed platform with ``--platform <x>``.

Every run, dry or real, observes the outgoing POST, verifies it against EXPECTED, and
saves the decoded payload as ``runs/<ts>/<platform>-payload.json`` — the same proof the
test suite asserts.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import Request, Route, sync_playwright

from .driver import FILLERS
from .product import ASSET_PATHS, BASE_URL, FORM_ACTION_GLOB
from .submission import check_submission, decode_payload

PLATFORM_ORDER = ("market", "studio", "procurement")


def _swallow(route: Route) -> None:
    route.fulfill(status=200, body="")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="w75-listing", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--platform", choices=("all", *PLATFORM_ORDER), default="all")
    parser.add_argument("--submit", action="store_true", help="let the Google-Form POST through (REAL submission)")
    parser.add_argument("--headed", action="store_true", help="show the browser window")
    parser.add_argument("--runs-dir", type=Path, default=Path("runs"))
    args = parser.parse_args(argv)

    platforms = PLATFORM_ORDER if args.platform == "all" else (args.platform,)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.runs_dir / (stamp if args.submit else f"{stamp}-dry")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[w75] {'SUBMIT' if args.submit else 'dry run (POST intercepted)'} → {out_dir}")

    ids: dict[str, str] = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        context = browser.new_context(base_url=BASE_URL, locale="zh-TW", viewport={"width": 1440, "height": 900})
        if not args.submit:
            context.route(FORM_ACTION_GLOB, _swallow)
        for platform in platforms:
            page = context.new_page()
            bodies: list[str] = []

            def observe(request: Request) -> None:  # observes only; the route above decides delivery
                if request.url.endswith("/formResponse"):
                    bodies.append(request.post_data or "")

            page.on("request", observe)
            try:
                submission_id = FILLERS[platform](page, ASSET_PATHS)
            except Exception as exc:  # noqa: BLE001 — CLI boundary: report, screenshot, stop
                page.screenshot(path=str(out_dir / f"{platform}-FAILED.png"), full_page=True)
                first_line = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
                print(f"[w75] {platform}: FAILED — {first_line}", file=sys.stderr)
                browser.close()
                return 1
            page.screenshot(path=str(out_dir / f"{platform}.png"), full_page=True)
            page.close()
            ids[platform] = submission_id
            problems = ["no formResponse POST observed"] if len(bodies) != 1 else check_submission(bodies[0], platform, submission_id)
            if bodies:
                (out_dir / f"{platform}-payload.json").write_text(
                    json.dumps(decode_payload(bodies[0]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            if problems:
                print(f"[w75] {platform}: {submission_id} — PAYLOAD MISMATCH ({len(problems)}):", file=sys.stderr)
                for problem in problems:
                    print(f"[w75]   {problem}", file=sys.stderr)
                browser.close()
                return 1
            print(f"[w75] {platform}: {submission_id} — payload verified against EXPECTED, saved {platform}-payload.json, screenshot {platform}.png")
        browser.close()

    (out_dir / "submission-ids.txt").write_text("".join(f"{name}\t{sid}\n" for name, sid in ids.items()), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
