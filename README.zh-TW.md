# Miraform W75 — 沙盒上架驅動程式

[English](README.md) | 繁體中文

自動完成 **Computer Use** 課程任務 `https://miraform-w75-gmail-color-lab.ai-e4b4.chatgpt.site/`：
一個模擬的 Gmail 信箱要求學員 `MFW75-PRACTICE` 只用信中附的商品主檔與四張 PNG，把（虛構的）
Miraform W75 鍵盤上架到三個模擬平台 — QMarket（`/market`）、Store Studio（`/studio`）、
SupplyDesk（`/procurement`）。

本 repo 包含：資料轉錄、Playwright 驅動程式、一套**不會真的送出任何東西**就能端到端驗證
每個表單的 pytest 測試，以及執行那唯一一次真實提交的 CLI。

## 環境需求

- Python ≥ 3.12 與 [uv](https://docs.astral.sh/uv/)
- macOS／Linux／Windows，且允許下載 Chromium（Playwright 會抓自己的版本）
- 能連到沙盒主機（前面有 Cloudflare；headless Chromium 可通過）

## 安裝

```bash
uv sync                                   # 依 uv.lock 建立 .venv（playwright 1.62.0、pytest-playwright 0.9.0）
uv run python -m playwright install chromium
```

## 重現驗證（安全 — 不會送出任何資料）

```bash
uv run pytest -q                          # 10 個測試，約 11–20 秒
```

瀏覽器測試會打開**線上**沙盒頁面、填滿每個欄位、上傳四張 PNG、按下平台的送出鈕，並斷言
成功橫幅出現。頁面唯一的對外請求 — 送往課程 Google 表單的 `no-cors` POST — 會被 `intercept`
fixture（`tests/conftest.py`）攔截：擷取內容後回 `200`，頁面因此進入成功狀態，但沒有任何
資料離開本機。擷取到的 payload 再與 `src/w75_listing/product.py` 的 `EXPECTED[platform]`
做**完全相等**比對。

| 測試 | 證明什麼 |
|---|---|
| `tests/test_assets.py` | 內附 PNG 的 SHA-256 與 `assets/asset-manifest.csv` 逐一相符且順序正確 |
| `tests/test_product.py` | 資料防呆：GTIN 維持 `未申請`、賣點不含售價／免運／認證宣稱、SKU／售價／庫存一致 |
| `tests/test_market.py` | 四步驟精靈、`素材已辨識`、`4 張教材素材順序正確`、成功橫幅 + UUID、payload == 預期 |
| `tests/test_studio.py` | 單頁表單（含狀態／通路／課稅），payload == 預期 |
| `tests/test_procurement.py` | A–E 區段、6 列 BOM、4 項聲明，payload == 預期 |

常用參數（來自 `pytest-playwright`）：`--headed` 看畫面、`--tracing on` 錄製。失敗時 trace
與截圖留在 `test-results/`。

## 試跑 vs. 真實提交

```bash
uv run python -m w75_listing              # 試跑：與測試相同的攔截；不會送出
uv run python -m w75_listing --submit     # 真實提交：放行 POST — 每個平台送出一次
```

選項：`--platform {all,market,studio,procurement}`（只重跑單一平台）、`--headed`、
`--runs-dir DIR`。

每次執行會寫入 `runs/<UTC 時間戳>[-dry]/`：每個平台一張整頁截圖（`market.png`、`studio.png`、
`procurement.png`）與 `submission-ids.txt`。失敗時存 `<platform>-FAILED.png`、印出錯誤、
以 exit 1 結束且不碰其餘平台 — 用 `--platform` 只重跑那一個。`runs/` 已列入 git-ignore。

提交 ID 由前端產生（`crypto.randomUUID()`）並顯示在頁面上；網站送往的 Google 表單使用
佔位的 entry id，所以課程後端是否真的記錄了，從這裡無法觀察。頁面的成功橫幅是沙盒提供的
唯一證據。

## 資料從哪裡來

`assets/Miraform-W75-product-master.md`（信中附的課程資料包，連同四張 PNG 與
`asset-manifest.csv` 一起內附）是唯一來源，如任務信所要求。主檔未交代之處，轉錄採以下
判斷：Store Studio 狀態 `啟用`、通路只勾 `網路商店`、勾選課稅（主檔售價含 5% 營業稅）、
商品說明改寫自簡介與五項特色且不新增任何事實；SupplyDesk 固定六列 BOM 與主檔第 1–4、8 列
一對一對應，`消音材料` 把 PORON／IXPE／軟木合併為一列（數量 `各 1`）；標籤已標示單位的
數值欄位填純數字，SupplyDesk 未標單位的欄位填主檔原文（`1.18 kg`、`18 個月`、`NT$3,650`）。
`src/w75_listing/product.py` 的 `FIELDS` 是實際輸入的值（以每個 input 的 `name` 為鍵）；
`EXPECTED` 則是頁面由這些輸入組出的 payload，依網站自身 JavaScript 的組法重建。

## 驅動程式在這個網站上如何保持穩定

- **等待 hydration** — 這台主機的 React hydration 每個新瀏覽器 context 要 0.4 秒到一分多鐘
  不等；hydration 前的點擊會被靜默丟棄。`wait_hydrated()` 在任何互動前輪詢表單按鈕上的
  React `__reactProps` 屬性（上限 90 秒）。`load` 與 `networkidle` 在這裡都會卡住，故不使用。
- **精靈步驟** — QMarket 用 `display:none` 隱藏非當前面板；驅動程式先點側欄步驟並斷言面板
  `h1`（失敗則重點）再填寫。
- **定位器** — 以 `<form>` 內的 `name` 定位輸入欄（單獨的 `[name=description]` 也會命中
  `<meta name="description">`）。
- **上傳** — 對隱藏的 file input 用 `set_input_files`；頁面以 SHA-256 雜湊檔案，四張全部
  依序相符時才顯示 `素材已辨識`。

## 目錄結構

```
assets/                 課程資料包：4 張 PNG、asset-manifest.csv、商品主檔（md）
src/w75_listing/
  product.py            STUDENT、ASSET_ORDER、FIELDS、EXPECTED
  driver.py             wait_hydrated、goto_step、fill_fields、upload_assets、fill_*
  __main__.py           CLI（python -m w75_listing）
tests/                  conftest（intercept fixture）+ 5 個測試模組
runs/                   每次執行的截圖 + submission-ids.txt（git-ignore）
```

資料轉錄、驅動程式與測試框架的設計與決策紀錄（程式碼以 `AC<n>` 引用）→
`docs/w75-listing-rationale.zh-TW.md`（引用正本為英文版 `docs/w75-listing-rationale.md`）。
