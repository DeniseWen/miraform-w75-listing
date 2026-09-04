# Miraform W75 沙盒上架 — 設計與決策紀錄

[English](w75-listing-rationale.md) | 繁體中文

> 程式碼註解與測試 docstring 以 `AC<n>` 引用驗收條件。引用的正本是英文版
> `w75-listing-rationale.md`；本文是逐節對照的繁體中文譯本，標題編號與英文版一致。
> 內容於 2026-09-04 由該次任務的規劃檔（task_plan.md、findings.md、progress.md）
> 提煉而成；那些檔案只是單一工作階段的工作記憶，不予保留。

## 摘要

本 repo 自動完成一項課程任務：沙盒 `https://miraform-w75-gmail-color-lab.ai-e4b4.chatgpt.site/`
以模擬 Gmail 要求學員 `MFW75-PRACTICE` 把虛構的 Miraform W75 鍵盤上架到三個模擬平台 —
QMarket `/market`（四步驟精靈，19 個輸入欄）、Store Studio `/studio`（單頁，24 個輸入名稱）、
SupplyDesk `/procurement`（單頁，46 個輸入名稱 + 4 個聲明勾選框）— 三者使用同一組四張 PNG。
完成條件是每個平台各成功提交一次。

支撐整體設計的不變量，每一條都有 2026-09-04 的實測依據：

- **網站只驗證 `student` 一個欄位。** 每個頁面 chunk 唯一會擋下送出的檢查是
  `if(!FormData.get("student")) → error`；其餘內容照輸入原樣送出。因此「正確」指的是忠實轉錄，
  而不是通過某個驗證器。
- **唯一的對外請求是送往 Google 表單的 `no-cors` POST**，鍵為 `entry.00000001..05`。
  fetch 一 resolve 頁面就切到成功狀態，所以測試可以用 `route.fulfill(200)` 攔截，仍看到真正的
  成功橫幅。回應雖不透明，但該表單（「Miraform W75 多平台商品上架沙盒｜回覆後端」）恰有 id 1–5
  的五個必填題、與送出的內容一一對應，且預填探測顯示 Google 會把補零鍵解析到這些題目 — 因此
  完整的 POST 會被接受（2026-09-04 真實提交後量測）。
- **上傳在瀏覽器內做雜湊比對**：每個檔案的 SHA-256 與 4 筆清單比對；四張全對才顯示
  `素材已辨識`，QMarket 第 4 步另外檢查順序。內附的 PNG 與清單逐位元相同。
- **這台主機的 React hydration 慢且不穩** — 每個新瀏覽器 context 需 0.4 秒到 62 秒
  （實測 6 個 context），而 `load` 與 `networkidle` 各卡住過一次（30 秒逾時）。hydration 前的
  點擊會被靜默丟棄。驅動程式因此在碰任何表單前，先輪詢表單按鈕上的 React `__reactProps` 屬性。
- **QMarket 用 `display:none` 隱藏非當前面板**，所以只有在側欄步驟啟用、並以步驟 `h1` 斷言
  確認後，才填寫該面板。
- **輸入欄以 `<form>` 內的 `name` 定位**：除了勾選框群組（`channel`、`declaration`）外每頁名稱
  唯一，而單獨的 `[name=description]` 也會命中 `<meta name="description">`。
- **商品主檔 md 是唯一資料來源**（任務信禁止其他來源）；主檔未交代的四項判斷記錄在下方
  AC4 與 AC5。
- **真實提交只做一次、須明確同意、headless、與測試同一套驅動程式**（`--submit` 移除攔截）；
  失敗的平台以 `--platform` 單獨重跑。已於 2026-09-04 14:27 執行 — ID 見工作階段索引。

## 驗收條件（最終版本，2026-09-04 核准）

- AC1: 給定 `assets/` 內有課程資料包的 4 張 PNG 與 `asset-manifest.csv`，當 `tests/test_assets.py` 計算每個檔案的 SHA-256，則每個雜湊值等於清單中該檔名的那一列，且 `ASSET_ORDER` 依 01→04 列出。
- AC2: 給定 `src/w75_listing/product.py` 的 `EXPECTED`，當 `tests/test_product.py` 執行（不開瀏覽器），則 `procurement.identity.gtin == "未申請"`、market `highlights` 不含 `NT$`／`免運`／`認證`、所有售價為 `"4680"`、SKU 為 `MFW75-WN-DN`／`MFW75-WN-MS`、庫存為 `"36"`／`"24"`，且 `STUDENT == "MFW75-PRACTICE"`。
- AC3: 給定 `/market` 已開啟且 Google 表單 POST 被攔截，當 `fill_market(page, assets)` 走完步驟 1–4 並依清單順序上傳 4 張 PNG，則步驟 3 顯示「素材已辨識」、步驟 4 顯示「4 張教材素材順序正確」、按下「確認並上架商品」後頁面顯示「沙盒商品已上架」與 `<code>` 內的 UUID v4，且攔截到的內容解出 `entry.00000001 == "MFW75-PRACTICE"`、`entry.00000002 == "quick-market"`、`json.loads(entry.00000003)["data"] == EXPECTED["market"]`。
- AC4: 給定 `/studio` 已開啟且 POST 被攔截，當 `fill_studio(page, assets)` 填滿全部 24 個具名欄位（狀態 `啟用`、通路只勾 `網路商店`、勾選課稅）並上傳 4 張 PNG，則頁面顯示「商品已儲存」與 UUID v4，且攔截到的 payload 平台為 `brand-studio`、`data == EXPECTED["studio"]`。
- AC5: 給定 `/procurement` 已開啟且 POST 被攔截，當 `fill_procurement(page, assets)` 填滿 A–E 區段（6 列 BOM、4 項聲明全勾）並上傳 4 張 PNG，則頁面顯示「採購料號已送審」與 UUID v4，且攔截到的 payload 平台為 `procurement-grid`、`len(data["declarations"]) == 4`、`data == EXPECTED["procurement"]`。
- AC6: 給定任一表單測試，當它結束時，則攔截 fixture 回報恰好一次已回應的 `formResponse` 請求，且 `page.on("request")` 紀錄中沒有任何未被攔截、送往 `docs.google.com` 的請求。
- AC7: 給定 `uv run python -m w75_listing --submit`，當對線上網站執行一次，則印出三個提交 ID（market → studio → procurement）並寫出 `runs/<UTC 時間戳>/{market,studio,procurement}.png` 成功截圖。（會真的送出 — 只執行一次，且僅在使用者明確同意後。）

## 目錄

資料
- [AC1 — 內附素材即課程資料包，且依清單順序](#ac1--內附素材即課程資料包且依清單順序)
- [AC2 — 資料防呆：不捏造、不矛盾](#ac2--資料防呆不捏造不矛盾)

表單
- [AC3 — QMarket 精靈端到端](#ac3--qmarket-精靈端到端)
- [AC4 — Store Studio 單頁，含主檔未交代的欄位](#ac4--store-studio-單頁含主檔未交代的欄位)
- [AC5 — SupplyDesk 資料表：BOM 對應、單位、聲明](#ac5--supplydesk-資料表bom-對應單位聲明)

測試框架
- [AC6 — 測試期間沒有任何請求離開本機](#ac6--測試期間沒有任何請求離開本機)

附錄
- [工作階段索引](#工作階段索引)

## AC1 — 內附素材即課程資料包，且依清單順序

**結論。** 四張 PNG、`asset-manifest.csv` 與商品主檔 md 都提交在 `assets/` 下；`ASSET_ORDER` 即清單順序 01→04。
**原因。** 頁面只靠 SHA-256 比對清單來辨識上傳，QMarket 在順序不同時會警告 — 所以位元組與順序都是契約的一部分。選擇內附（6.9 MB）而非抓取腳本或測試時下載，是為了讓雜湊測試與表單測試除了沙盒本身之外不再依賴任何網路。
**約束。** `src/w75_listing/product.py:ASSET_ORDER`、`:ASSET_PATHS`；`src/w75_listing/driver.py:upload_assets`（依該順序上傳並等待 `.asset-ok`）。
**證據。** `tests/test_assets.py::test_every_png_matches_manifest_sha256`、`::test_asset_order_follows_manifest`；2026-09-04 對解壓後的課程資料包執行 `shasum -a 256`，4/4 相符。
**被取代於。** —

## AC2 — 資料防呆：不捏造、不矛盾

**結論。** `EXPECTED` 由 `assets/Miraform-W75-product-master.md` 手動轉錄成 `FIELDS`，再依網站自身 chunk 的組法重建成三種 payload 形狀；防呆測試釘住任務信點名的陷阱。
**原因。** 任務信要求只用信件與附件，並說 GTIN「尚未申請 … 不可自行編造」。網站 JS 內另有一份商品物件，其 BOM 用語在兩列與 md 不同；學員被告知使用的是 md，故以 md 為準。賣點是五行「主要賣點」原文 — QMarket 的 textarea 禁止售價、免運與認證宣稱，而那五行都沒有。
**約束。** `src/w75_listing/product.py:FIELDS`、`:EXPECTED`、`:_market_payload`、`:_studio_payload`、`:_procurement_payload` — 三個組建函式必須鏡射頁面 chunk 組出的 payload 鍵（`variants[].option`、`pricing.taxable`、`shipping.physical/unit`、`bom[].section`、`imageOrder`／`mediaOrder`／`attachments`）。
**證據。** `tests/test_product.py`（5 個測試）；AC3–AC5 的完全相等斷言，是組建函式與網站一致的端到端證明。
**被取代於。** —

## AC3 — QMarket 精靈端到端

**結論。** `fill_market` 先等 hydration，再對步驟 1–3 逐一：點側欄步驟、斷言面板 `h1`、以 name 填該面板的輸入欄、在步驟 3 上傳並斷言 `素材已辨識`；接著到步驟 4 斷言 `4 張教材素材順序正確`、送出，並回傳 `<code>` 內的 UUID。
**原因。** 面板在啟用前是 `display:none`，對隱藏輸入欄 `fill()` 會逾時；步驟點擊是冪等的，但在 hydration 前會被丟棄（單靠 `domcontentloaded` 時 4 次有 1 次），所以 `h1` 斷言加上重點讓遺失的點擊立刻失敗。`networkidle` 試過但在 13 次中卡住 1 次後放棄；`load` 也卡住 — 因此改用 `wait_hydrated`，輪詢 `__reactProps` 鍵、上限 90 秒（實測 hydration 0.4–62 秒）。第一次真實提交正是在這裡、在任何 POST 之前失敗；修正後先重跑整套測試與試跑驗證，才再次執行真實提交。
**約束。** `src/w75_listing/driver.py:wait_hydrated`（`JS_FORM_HYDRATED`、`HYDRATION_TIMEOUT_MS`）、`:goto_step`（`STEP_RETRIES`、`STEP_TIMEOUT_MS`）、`:MARKET_STEPS`（哪個輸入欄屬於哪個面板）、`:fill_market`。
**證據。** `tests/test_market.py::test_market_listing_submits_expected_payload`；2026-09-04 14:27 真實提交 ID `0a196429-4961-4afe-ac8e-60983fdcfc24`。
**被取代於。** —

## AC4 — Store Studio 單頁，含主檔未交代的欄位

**結論。** 24 個具名欄位一次填完、上傳四張 PNG、按下 `儲存商品`。主檔未交代之處：狀態 `啟用`、銷售通路只勾 `網路商店`、勾選 `此商品需課稅`，商品說明是 254 字、由簡介加五項特色改寫而成；商品重量填商品淨重 `1.18`。
**原因。** 主檔售價註明含 5% 營業稅，故勾選課稅；未在網路商店 `啟用` 的商品不算完成上架；說明欄自己的 placeholder 禁止照抄來源，而改寫文字沒有任何主檔以外的事實（每個片語都對照過 md）。「商品重量（kg）」指的是商品而非包裹 — 主檔淨重 1.18 kg，含包裝重量 1.65 kg（用於 AC3 的含包裝重量與 AC5 的單件含包裝重量）。
**約束。** `src/w75_listing/product.py:FIELDS["studio"]`、`:DESCRIPTION`；`src/w75_listing/driver.py:_fill_single_page`、`:fill_studio`；`control()` 限定在 form 內，因為 `<meta name="description">` 會與 textarea 撞名。
**證據。** `tests/test_studio.py::test_studio_listing_submits_expected_payload`；真實提交 ID `24f9d24b-72b6-44e5-aece-cd767b39bc1e`。
**被取代於。** —

## AC5 — SupplyDesk 資料表：BOM 對應、單位、聲明

**結論。** A–E 區段以 name 填寫；表單固定的六列 BOM（外殼／內骨架／PCB／定位板／消音材料／電池）與主檔第 1–4、8 列一對一對應，`消音材料` 把 PORON 夾心棉、IXPE 軸下墊、天然軟木底墊合併為一列、數量 `各 1`；主檔的鍵帽與腳墊兩列沒有對應區段，予以省略。`採購商品名稱` 填主檔的商品名稱、不含品牌（表單另有製造商／品牌欄）。GTIN 為 `未申請`。四項聲明全部勾選，因為每一項在主檔中都為真。標籤未標單位的數值欄位填主檔原文（`1.18 kg`、`18 個月`、`NT$3,650`、`12 把`）。
**原因。** 表單寫著「無資料的欄位不可猜測」：把三種消音材料歸為一列是對應而非發明，`各 1` 陳述主檔給的數量而不捏造總數；未標單位的欄位若填純數字就會丟失主檔標明的單位，而 QMarket／Studio 標籤已標單位的欄位（`保固（月）`、`商品重量（kg）`）則填純數字。
**約束。** `src/w75_listing/product.py:FIELDS["procurement"]`、`:BOM_SECTIONS`、`:DECLARATIONS`、`:_procurement_payload`；`src/w75_listing/driver.py:fill_procurement`。
**證據。** `tests/test_procurement.py::test_procurement_sheet_submits_expected_payload`；真實提交 ID `600a55ae-03ed-492e-88ec-3269476417db`（整頁截圖顯示橫幅「採購料號已送審 · 三個平台任務全部完成」）。
**被取代於。** —

## AC6 — 測試期間沒有任何請求離開本機

**結論。** `page.route("**/formResponse")` 擷取內容並回應 `200`；`page.on("request")` 紀錄必須恰好含一個 `docs.google.com` 請求，且必須就是被攔截的那一個。
**原因。** `route.abort()` 會讓頁面的 fetch 拋出例外並落入其 `catch → error` 狀態，測試就會在斷言一個真實提交永遠不會出現的狀態；改為回應 200，頁面能到達與正式提交相同的成功橫幅，同時沒有任何資料外流。擷取到的內容是 url-encoded 的表單 entry，其中 `entry.00000003` 是 payload JSON — 與 `EXPECTED` 做完全相等斷言，因為 `data` 純粹由我們控制的 `FormData` 值組成（未填的文字欄 → `""`，未選的 select → `null`）。
**約束。** `tests/conftest.py:intercept`、`:Intercept.assert_clean`；`src/w75_listing/product.py:FORM_ACTION_GLOB`；CLI 試跑在 context 層級重用同一個 glob（`src/w75_listing/__main__.py:_swallow`）。解碼與逐欄檢查放在 `src/w75_listing/submission.py`（`decode_entries`、`decode_payload`、`check_submission`），由 fixture 與 CLI 共用，因此真實提交也會留下以同樣方式驗證過的 `runs/<ts>/<platform>-payload.json`。
**證據。** 每個表單測試都呼叫 `intercept.assert_clean()`；2026-09-04 的攔截煙霧測試擷取到五個 entry（student、platform、payload、assets、version `1.0.0`）與一個被攔截的請求。
**被取代於。** —

## 工作階段索引

- 2026-09-04 — 唯讀分析、規劃三件套、7 輪 grilling（25 項決策）、以 uv + playwright 1.62.0 建立骨架、資料層、驅動程式與測試（10 個全綠）、CLI、試跑、第一次 `--submit` 在 market 步驟 2、任何 POST 之前失敗（hydration）、加入 `wait_hydrated`、14:27 真實提交成功（ID：market `0a196429-4961-4afe-ac8e-60983fdcfc24`、studio `24f9d24b-72b6-44e5-aece-cd767b39bc1e`、procurement `600a55ae-03ed-492e-88ec-3269476417db`）、pyright 無錯誤、README。
