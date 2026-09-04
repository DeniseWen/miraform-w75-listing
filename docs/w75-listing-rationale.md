# Miraform W75 sandbox listing — design & rationale

English | [繁體中文](w75-listing-rationale.zh-TW.md)

> Code comments and test docstrings cite acceptance criteria in this doc as `AC<n>`.
> Distilled 2026-09-04 from the task's planning files (task_plan.md, findings.md,
> progress.md); those files were the working memory of one session and are not kept.

## Abstract

The repo automates one course task: the sandbox at
`https://miraform-w75-gmail-color-lab.ai-e4b4.chatgpt.site/` shows a simulated Gmail
asking student `MFW75-PRACTICE` to list the fictional Miraform W75 keyboard on three
simulated platforms — QMarket `/market` (4-step wizard, 19 inputs), Store Studio
`/studio` (single page, 24 input names), SupplyDesk `/procurement` (single page, 46 input
names + 4 declaration boxes) — each with the same four PNGs. Completion means one
successful submit per platform.

Load-bearing invariants, each backed by a measurement made on 2026-09-04:

- **The site validates nothing but `student`.** Each page chunk's only blocking check is
  `if(!FormData.get("student")) → error`; everything else is posted as typed. Correctness
  therefore means faithful transcription, not passing a validator.
- **The only outbound call is a `no-cors` POST to a Google Form** with keys
  `entry.00000001..05`. The page flips to its success state when the fetch resolves, so a
  test can `route.fulfill(200)` it and still reach the real success banner. The response is
  opaque, but the form (「Miraform W75 多平台商品上架沙盒｜回覆後端」) has exactly five
  required questions with ids 1–5 matching what is sent, and a prefill probe showed Google
  resolves the zero-padded keys to them — so a complete POST is accepted (measured
  2026-09-04, after the real run).
- **Uploads are hash-checked in the browser**: SHA-256 of each file is matched to a
  4-entry manifest; `素材已辨識` appears only when all four match, and QMarket's step 4
  additionally checks the order. The vendored PNGs are byte-identical to the manifest.
- **React hydration on this host is slow and erratic** — 0.4 s to 62 s per fresh browser
  context (6 contexts measured), and both `load` and `networkidle` hung once (30 s
  timeouts). A click before hydration is dropped silently. The driver therefore polls
  for React's `__reactProps` expando on a form button before touching any form.
- **QMarket hides inactive wizard panels with `display:none`**, so a panel is filled only
  after its sidebar step is active, asserted via the step `h1`.
- **Inputs are addressed by `name` inside `<form>`**: names are unique per page except the
  checkbox groups (`channel`, `declaration`), and a bare `[name=description]` also matches
  `<meta name="description">`.
- **The master md is the sole data source** (the email forbids anything else); the four
  judgment calls it leaves open are recorded under AC4 and AC5 below.
- **One real submission, on explicit go, headless, same driver as the tests** (`--submit`
  removes the intercept); a failed platform is re-run alone with `--platform`. Performed
  2026-09-04 14:27 — ids in the session index.

## Acceptance criteria (final wording, approved 2026-09-04)

- AC1: Given `assets/` holds the 4 PNGs and `asset-manifest.csv` from the course pack, When `tests/test_assets.py` computes SHA-256 of each file, Then every hash equals the manifest row for that filename and `ASSET_ORDER` lists them 01→04.
- AC2: Given `EXPECTED` in `src/w75_listing/product.py`, When `tests/test_product.py` runs (no browser), Then `procurement.identity.gtin == "未申請"`, market `highlights` contain none of `NT$` / `免運` / `認證`, every price is `"4680"`, SKUs are `MFW75-WN-DN` / `MFW75-WN-MS`, stocks `"36"` / `"24"`, and `STUDENT == "MFW75-PRACTICE"`.
- AC3: Given `/market` opened with the Google-Form POST intercepted, When `fill_market(page, assets)` drives steps 1–4 and uploads the 4 PNGs in manifest order, Then step 3 shows "素材已辨識", step 4 shows "4 張教材素材順序正確", after "確認並上架商品" the page shows "沙盒商品已上架" plus a UUID v4 in `<code>`, and the intercepted body decodes to `entry.00000001 == "MFW75-PRACTICE"`, `entry.00000002 == "quick-market"`, `json.loads(entry.00000003)["data"] == EXPECTED["market"]`.
- AC4: Given `/studio` opened with the POST intercepted, When `fill_studio(page, assets)` fills all 24 named fields (status `啟用`, channel `網路商店` only, taxable checked) and uploads the 4 PNGs, Then the page shows "商品已儲存" plus a UUID v4, and the intercepted payload has platform `brand-studio` and `data == EXPECTED["studio"]`.
- AC5: Given `/procurement` opened with the POST intercepted, When `fill_procurement(page, assets)` fills sections A–E (6 BOM rows, all 4 declarations checked) and uploads the 4 PNGs, Then the page shows "採購料號已送審" plus a UUID v4, and the intercepted payload has platform `procurement-grid`, `len(data["declarations"]) == 4`, and `data == EXPECTED["procurement"]`.
- AC6: Given any form test, When it finishes, Then the intercept fixture reports exactly one fulfilled `formResponse` request and the `page.on("request")` log contains no un-routed request to `docs.google.com`.
- AC7: Given `uv run python -m w75_listing --submit`, When run once against the live site, Then it prints three submission IDs (market → studio → procurement) and writes `runs/<UTC timestamp>/{market,studio,procurement}.png` success screenshots. (Executes real submissions — run once, only on explicit user go.)

## Contents

Data
- [AC1 — vendored assets are the course pack, in manifest order](#ac1--vendored-assets-are-the-course-pack-in-manifest-order)
- [AC2 — data guards: nothing fabricated, nothing inconsistent](#ac2--data-guards-nothing-fabricated-nothing-inconsistent)

Forms
- [AC3 — QMarket wizard end to end](#ac3--qmarket-wizard-end-to-end)
- [AC4 — Store Studio single page, incl. the fields the master leaves open](#ac4--store-studio-single-page-incl-the-fields-the-master-leaves-open)
- [AC5 — SupplyDesk sheet: BOM mapping, units, declarations](#ac5--supplydesk-sheet-bom-mapping-units-declarations)

Harness
- [AC6 — no request leaves the machine during tests](#ac6--no-request-leaves-the-machine-during-tests)

Appendix
- [Session index](#session-index)

## AC1 — vendored assets are the course pack, in manifest order

**Verdict.** The four PNGs, `asset-manifest.csv`, and the product master md are committed under `assets/`; `ASSET_ORDER` is the manifest order 01→04.
**Why.** The page recognises an upload only by SHA-256 against the manifest, and QMarket warns when the order differs — so the bytes and the order are both part of the contract. Vendoring (6.9 MB) was chosen over a fetch script or a test-time download so the hash test and the form tests need no extra network dependency beyond the sandbox itself.
**Constrains.** `src/w75_listing/product.py:ASSET_ORDER`, `:ASSET_PATHS`; `src/w75_listing/driver.py:upload_assets` (uploads in that order and waits for `.asset-ok`).
**Evidence.** `tests/test_assets.py::test_every_png_matches_manifest_sha256`, `::test_asset_order_follows_manifest`; `shasum -a 256` of the unzipped course pack matched 4/4 on 2026-09-04.
**Superseded by.** —

## AC2 — data guards: nothing fabricated, nothing inconsistent

**Verdict.** `EXPECTED` is hand-transcribed from `assets/Miraform-W75-product-master.md` into `FIELDS`, then rebuilt into the three payload shapes the way the site's own chunks do it; guards pin the traps the email names.
**Why.** The email says to use only the mail and its attachments, and that the GTIN "尚未申請 … 不可自行編造". The site's JS carries its own copy of the product object whose BOM wording differs from the md in two rows; the md is what the student is told to use, so the md wins. Highlights are the five 主要賣點 lines verbatim — QMarket's textarea forbids price, free-shipping and certification claims, and those lines contain none.
**Constrains.** `src/w75_listing/product.py:FIELDS`, `:EXPECTED`, `:_market_payload`, `:_studio_payload`, `:_procurement_payload` — the three builders must mirror the payload keys the page chunks build (`variants[].option`, `pricing.taxable`, `shipping.physical/unit`, `bom[].section`, `imageOrder`/`mediaOrder`/`attachments`).
**Evidence.** `tests/test_product.py` (5 tests); the exact-equality assertions in AC3–AC5 are the end-to-end proof that the builders match the site.
**Superseded by.** —

## AC3 — QMarket wizard end to end

**Verdict.** `fill_market` waits for hydration, then for each of steps 1–3 clicks the sidebar step, asserts the panel `h1`, fills that panel's inputs by name, uploads on step 3, asserts `素材已辨識`, moves to step 4, asserts `4 張教材素材順序正確`, submits, and returns the UUID from `<code>`.
**Why.** Panels are `display:none` until active, so `fill()` on a hidden input would time out; the step click is idempotent but is dropped before hydration (1 in 4 with `domcontentloaded` alone), so the `h1` assertion with a click retry makes a lost click fail fast. `networkidle` was tried and rejected after it hung once in 13 attempts; `load` hung too — hence `wait_hydrated`, which polls for a `__reactProps` key with a 90 s ceiling (hydration measured 0.4–62 s). The first real run failed exactly here before any POST; the fix was verified by a fresh suite run and a dry run before the real run was repeated.
**Constrains.** `src/w75_listing/driver.py:wait_hydrated` (`JS_FORM_HYDRATED`, `HYDRATION_TIMEOUT_MS`), `:goto_step` (`STEP_RETRIES`, `STEP_TIMEOUT_MS`), `:MARKET_STEPS` (which input belongs to which panel), `:fill_market`.
**Evidence.** `tests/test_market.py::test_market_listing_submits_expected_payload`; real run 2026-09-04 14:27 id `0a196429-4961-4afe-ac8e-60983fdcfc24`.
**Superseded by.** —

## AC4 — Store Studio single page, incl. the fields the master leaves open

**Verdict.** All 24 named fields are filled in one pass, four PNGs uploaded, `儲存商品` clicked. Where the master is silent: status `啟用`, sales channel `網路商店` only, `此商品需課稅` checked, and 商品說明 is a 254-character paraphrase of the summary plus the five highlights; 商品重量 is the product net weight `1.18`.
**Why.** The master prices are stated as 含 5% 營業稅, so taxable is on; a listing that is not 啟用 on the 網路商店 would not be a completed listing; the description field's own placeholder forbids copying the source verbatim, and the paraphrase carries no fact absent from the master (each phrase was checked against the md). 商品重量（kg） names the product, not the parcel — the master's 淨重 is 1.18 kg, its 含包裝重量 1.65 kg (used by AC3's shipping weight and AC5's 單件含包裝重量).
**Constrains.** `src/w75_listing/product.py:FIELDS["studio"]`, `:DESCRIPTION`; `src/w75_listing/driver.py:_fill_single_page`, `:fill_studio`; `control()` is form-scoped because `<meta name="description">` collides with the textarea.
**Evidence.** `tests/test_studio.py::test_studio_listing_submits_expected_payload`; real run id `24f9d24b-72b6-44e5-aece-cd767b39bc1e`.
**Superseded by.** —

## AC5 — SupplyDesk sheet: BOM mapping, units, declarations

**Verdict.** Sections A–E filled by name; the form's six fixed BOM rows (外殼 / 內骨架 / PCB / 定位板 / 消音材料 / 電池) take the master's rows 1–4 and 8 one-to-one, with 消音材料 combining PORON 夾心棉、IXPE 軸下墊、天然軟木底墊 as one row of quantity `各 1`; the master's 鍵帽 and 腳墊 rows have no section and are omitted. `採購商品名稱` is the master's 商品名稱 without the brand (the sheet has its own 製造商／品牌 field). GTIN is `未申請`. All four declarations are ticked because each is true in the master. Numeric fields whose label omits the unit carry the master's own text (`1.18 kg`, `18 個月`, `NT$3,650`, `12 把`).
**Why.** The sheet says "無資料的欄位不可猜測": grouping the three damping materials is a mapping, not an invention, and `各 1` states the count the master gives without inventing a total; unit-less labels would otherwise lose the unit the master states, while QMarket/Studio labels that name the unit (`保固（月）`, `商品重量（kg）`) get bare numbers.
**Constrains.** `src/w75_listing/product.py:FIELDS["procurement"]`, `:BOM_SECTIONS`, `:DECLARATIONS`, `:_procurement_payload`; `src/w75_listing/driver.py:fill_procurement`.
**Evidence.** `tests/test_procurement.py::test_procurement_sheet_submits_expected_payload`; real run id `600a55ae-03ed-492e-88ec-3269476417db` (full-page screenshot shows the banner 採購料號已送審 · 三個平台任務全部完成).
**Superseded by.** —

## AC6 — no request leaves the machine during tests

**Verdict.** `page.route("**/formResponse")` captures the body and fulfils `200`; a `page.on("request")` log must contain exactly one `docs.google.com` request, and it must be the routed one.
**Why.** `route.abort()` would throw inside the page's fetch and land in its `catch → error` state, so tests would be asserting a state the real run never produces; fulfilling lets the page reach the same success banner as production while nothing leaves. The captured body is url-encoded form entries whose `entry.00000003` is the payload JSON — asserted for exact equality against `EXPECTED`, because `data` is built purely from `FormData` values we control (unfilled text → `""`, unfilled select → `null`).
**Constrains.** `tests/conftest.py:intercept`, `:Intercept.assert_clean`; `src/w75_listing/product.py:FORM_ACTION_GLOB`; the CLI's dry run reuses the same glob at context scope (`src/w75_listing/__main__.py:_swallow`). Decoding and the field-by-field check live in `src/w75_listing/submission.py` (`decode_entries`, `decode_payload`, `check_submission`), shared by the fixture and the CLI so a real run leaves `runs/<ts>/<platform>-payload.json` verified the same way.
**Evidence.** every form test calls `intercept.assert_clean()`; the intercept smoke on 2026-09-04 captured five entries (student, platform, payload, assets, version `1.0.0`) with one routed request.
**Superseded by.** —

## Session index

- 2026-09-04 — analysis (read-only), planning trio, 7 grilling rounds (25 decisions), scaffold with uv + playwright 1.62.0, data layer, driver + tests (10 green), CLI, dry run, first `--submit` failed at market step 2 before any POST (hydration), `wait_hydrated` added, real run succeeded 14:27 (ids: market `0a196429-4961-4afe-ac8e-60983fdcfc24`, studio `24f9d24b-72b6-44e5-aece-cd767b39bc1e`, procurement `600a55ae-03ed-492e-88ec-3269476417db`), pyright clean, README.
