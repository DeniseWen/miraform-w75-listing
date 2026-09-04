# Miraform W75 — sandbox listing driver

English | [繁體中文](README.zh-TW.md)

Automates the **Computer Use** course task at
`https://miraform-w75-gmail-color-lab.ai-e4b4.chatgpt.site/`: a simulated Gmail asks
student `MFW75-PRACTICE` to list the (fictional) Miraform W75 keyboard on three simulated
platforms — QMarket (`/market`), Store Studio (`/studio`), SupplyDesk (`/procurement`) —
using only the emailed product master and four PNGs.

The repo contains the data transcription, a Playwright driver, a pytest suite that proves
each form end to end **without** submitting anything, and a CLI that performs the one real
submission.

## Requirements

- Python ≥ 3.12 and [uv](https://docs.astral.sh/uv/)
- macOS/Linux/Windows with a Chromium download allowed (Playwright fetches its own build)
- Network access to the sandbox host (it sits behind Cloudflare; headless Chromium passes)

## Setup

```bash
uv sync                                   # creates .venv from uv.lock (playwright 1.62.0, pytest-playwright 0.9.0)
uv run python -m playwright install chromium
```

## Reproduce the verification (safe — nothing is submitted)

```bash
uv run pytest -q                          # 14 tests, ~45 s (12 browser-backed)
```

The browser tests open the **live** sandbox pages, fill every field, upload the four PNGs,
press the platform's submit button, and assert the success banner. The page's only
outbound call — a `no-cors` POST to the course Google Form — is intercepted by the
`intercept` fixture (`tests/conftest.py`), which captures the body and answers `200`, so
the page reaches its success state while nothing leaves the machine. The captured payload
is then compared **for exact equality** with `EXPECTED[platform]` in
`src/w75_listing/product.py`.

| Test | Proves |
|---|---|
| `tests/test_assets.py` | the vendored PNGs match `assets/asset-manifest.csv` SHA-256, in order |
| `tests/test_product.py` | data guards: GTIN stays `未申請`, highlights carry no price/免運/認證 claims, SKU/price/stock consistent |
| `tests/test_market.py` | 4-step wizard, `素材已辨識`, `4 張教材素材順序正確`, success banner + UUID, payload == expected |
| `tests/test_studio.py` | single-page form incl. status/channels/taxable, payload == expected |
| `tests/test_procurement.py` | sections A–E, 6 BOM rows, 4 declarations, payload == expected |
| `tests/test_submission.py` | the shared decoder/checker flags a wrong student, platform, id, or any `data` field |
| `tests/test_cli.py` | a CLI dry run writes `market-payload.json` equal to `EXPECTED` plus the screenshot and id |

Useful flags (from `pytest-playwright`): `--headed` to watch, `--tracing on` to record.
Failures leave a trace and screenshot under `test-results/`.

## Dry run vs. real run

```bash
uv run python -m w75_listing              # DRY RUN: same intercept as the tests; nothing submitted
uv run python -m w75_listing --submit     # REAL RUN: lets the POST through — one submission per platform
```

Options: `--platform {all,market,studio,procurement}` (re-run a single platform),
`--headed`, `--runs-dir DIR`.

Each run — dry or real — writes `runs/<UTC timestamp>[-dry]/` with, per platform, a
full-page screenshot (`<platform>.png`) and the decoded POST the page actually sent
(`<platform>-payload.json`), plus `submission-ids.txt`. The CLI observes that POST (it
only *intercepts* it in dry mode), checks it against `EXPECTED` field by field, and prints
`payload verified against EXPECTED` per platform. A mismatch prints every differing field
and exits 1; a driver failure saves `<platform>-FAILED.png` and exits 1 — in both cases the
remaining platforms are not touched, so re-run just that one with `--platform`. `runs/` is
git-ignored.

## How to verify a run

1. **The console line** `[w75] market: <uuid> — payload verified against EXPECTED, saved
   market-payload.json, screenshot market.png` means: the page showed its success banner
   with that id, and the body it POSTed decoded to exactly the expected fields.
2. **Open `runs/<ts>/<platform>.png`** — a full-page screenshot taken after submit: every
   field as filled, `素材已辨識 4/4`, the checked declarations, and the success banner with
   the same id at the bottom. This is the visual proof a viewer can check without running
   anything.
3. **Read `runs/<ts>/<platform>-payload.json`** — the `{submissionId, submittedAt,
   platform, data}` wrapper the site sent; `data` is what the course backend received.
4. **Re-run the suite** (`uv run pytest -q`, nothing submitted) or watch it
   (`--headed`) / replay it (`--tracing on`, then `uv run playwright show-trace
   test-results/<test>/trace.zip`).

What cannot be verified from here is the course's response sheet itself (owner-only);
see the note below on why a complete POST is accepted.

The submission IDs are generated client-side (`crypto.randomUUID()`) and shown on the
page once its POST has resolved. The response itself is opaque (`no-cors`), so the
recording cannot be read back from here — but the target Google Form (「Miraform W75
多平台商品上架沙盒｜回覆後端」) has exactly the five required questions the site sends
(學員識別碼, 平台代碼, 提交內容 JSON, 素材檔案驗證 JSON, 介面版本; ids 1–5), and Google
resolves the site's zero-padded keys `entry.00000001..05` to them (verified with a
prefill URL, which records nothing). A well-formed POST is therefore accepted; the
course owner's response sheet is where the rows land.

## Where the values come from

`assets/Miraform-W75-product-master.md` (the emailed course pack, vendored with its four
PNGs and `asset-manifest.csv`) is the sole source, as the task email requires. Where the
master is silent the transcription makes these calls: Store Studio status `啟用`, channel
`網路商店` only, taxable on (the master prices include 5% VAT), description paraphrased
from the summary and five highlights with no new facts; SupplyDesk's six fixed BOM rows map
1:1 to the master's rows 1–4 and 8, with 消音材料 combining PORON/IXPE/cork as one row
(qty `各 1`); numeric fields whose label names the unit get bare numbers, SupplyDesk's
unit-less labels get the master's own text (`1.18 kg`, `18 個月`, `NT$3,650`). `FIELDS`
in `src/w75_listing/product.py` is what gets typed, keyed by each input's `name`;
`EXPECTED` is the payload the page builds from those inputs, reconstructed the way the
site's own JavaScript does it.

## How the driver stays reliable on this site

- **Hydration wait** — React hydration on this host takes anywhere from 0.4 s to over a
  minute per fresh browser context; clicks before hydration are dropped silently.
  `wait_hydrated()` polls for React's `__reactProps` expando on a form button (90 s
  ceiling) before any interaction. `load` and `networkidle` both hang here, so they are
  not used.
- **Wizard steps** — QMarket hides inactive panels with `display:none`; the driver clicks
  the sidebar step and asserts the panel `h1` (retrying the click) before filling.
- **Locators** — inputs are addressed by `name` inside the `<form>` (a bare
  `[name=description]` also matches `<meta name="description">`).
- **Uploads** — `set_input_files` on the hidden file input; the page hashes the files with
  SHA-256 and shows `素材已辨識` only when all four match the manifest in order.

## Layout

```
assets/                 course pack: 4 PNG, asset-manifest.csv, product master (md)
src/w75_listing/
  product.py            STUDENT, ASSET_ORDER, FIELDS, EXPECTED
  driver.py             wait_hydrated, goto_step, fill_fields, upload_assets, fill_*
  submission.py         decode_entries, decode_payload, check_submission (shared by tests + CLI)
  __main__.py           CLI (python -m w75_listing)
tests/                  conftest (intercept fixture) + 7 test modules
runs/                   per-run screenshots, <platform>-payload.json, submission-ids.txt (git-ignored)
```

Design & rationale for the data transcription, driver and test harness (cited from code as `AC<n>`) → `docs/w75-listing-rationale.md` (繁體中文: `docs/w75-listing-rationale.zh-TW.md`).
