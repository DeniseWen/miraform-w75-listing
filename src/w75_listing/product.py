"""Miraform W75 listing data.

Every value below is transcribed from ``assets/Miraform-W75-product-master.md`` (the
only source the task email allows); judgment calls are the ones recorded in
``task_plan.md`` § Decisions Made. ``FIELDS`` is what the driver types into each form
(keyed by the input ``name``); ``EXPECTED`` is the ``data`` object the page builds from
those inputs and POSTs, reconstructed the same way the page chunks do it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

STUDENT = "MFW75-PRACTICE"
BASE_URL = "https://miraform-w75-gmail-color-lab.ai-e4b4.chatgpt.site"
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
ASSET_ORDER = (
    "miraform-w75-01-hero.png",
    "miraform-w75-02-top.png",
    "miraform-w75-03-connectivity.png",
    "miraform-w75-04-package.png",
)
ASSET_PATHS = [ASSETS_DIR / name for name in ASSET_ORDER]

PLATFORM_IDS = {"market": "quick-market", "studio": "brand-studio", "procurement": "procurement-grid"}
SUCCESS_TEXT = {"market": "沙盒商品已上架", "studio": "商品已儲存", "procurement": "採購料號已送審"}
FORM_ACTION_GLOB = "**/formResponse"

TITLE = "Miraform W75 胡桃木三模熱插拔機械鍵盤｜75% 配列・無刻 PBT 鍵帽"
CATEGORY_PATH = "電腦與周邊設備 > 電腦輸入裝置 > 鍵盤 > 機械鍵盤"
ORIGIN = "越南（台灣設計、越南組裝）"
HIGHLIGHTS = (
    "CNC 精密切削美國黑胡桃木外殼，每件木紋皆為自然生成",
    "2.4 GHz、Bluetooth 5.3、USB-C 有線三模連線",
    "75% ANSI 84 鍵配置，支援 3-pin／5-pin MX 軸熱插拔",
    "Gasket 結構、聚碳酸酯定位板、軟木與 PORON 多層消音",
    "奶油白／鼠尾草綠無刻 PBT 鍵帽，支援 Windows、macOS、Linux",
)
# Paraphrase of 商品簡介 + 五項特色 (Store Studio forbids a verbatim copy); no fact outside the md.
DESCRIPTION = (
    "Miraform W75 是一把 75% ANSI 84 鍵配置的三模熱插拔機械鍵盤。"
    "外殼以 CNC 精密切削美國黑胡桃木製成，每一把木紋皆為自然生成；"
    "內部採鋁合金內骨架與 Gasket 結構，搭配聚碳酸酯定位板、軟木與 PORON 多層消音。"
    "支援 2.4 GHz、Bluetooth 5.3 與 USB-C 有線三種連線，相容 Windows、macOS、Linux；"
    "軸座支援 3-pin／5-pin MX 軸熱插拔。"
    "標配奶油白／鼠尾草綠無刻 PBT 鍵帽，適合重視桌面質感、長時間輸入與可維修性的使用者。"
)
PACKAGE_CONTENTS = (
    "Miraform W75 鍵盤 × 1",
    "1.5 m 編織 USB-C to USB-C 線 × 1",
    "USB-C to USB-A 轉接頭 × 1",
    "2.4 GHz USB 接收器 × 1",
    "鋼絲拔鍵器 × 1",
    "金屬拔軸器 × 1",
    "備用無刻鍵帽 × 6",
    "快速入門卡 × 1",
    "再生紙漿內托與牛皮紙盒 × 1",
)
DECLARATIONS = ("內含可充電式鋰聚合物電池", "商品不防水", "GTIN 未申請", "木紋存在自然差異")
BOM_SECTIONS = ("外殼", "內骨架", "PCB", "定位板", "消音材料", "電池")

FieldValue = str | bool | list[str]

# Values keyed by input name. Selects hold the option label; checkbox groups hold the
# values to tick; single checkboxes hold a bool. Numeric fields whose label names the
# unit get bare numbers; SupplyDesk's unit-less labels get the md's own text.
FIELDS: dict[str, dict[str, FieldValue]] = {
    "market": {
        "student": STUDENT,
        "category": "電腦與周邊設備 / 鍵盤 / 機械鍵盤",
        "title": TITLE,
        "brand": "Miraform",
        "model": "MF-W75",
        "condition": "全新",
        "dawnSku": "MFW75-WN-DN",
        "dawnPrice": "4680",
        "dawnStock": "36",
        "mossSku": "MFW75-WN-MS",
        "mossPrice": "4680",
        "mossStock": "24",
        "highlights": "\n".join(HIGHLIGHTS),
        "origin": ORIGIN,
        "warranty": "18",
        "weight": "1.65",
        "length": "39.5",
        "width": "19.5",
        "height": "7.2",
    },
    "studio": {
        "title": TITLE,
        "description": DESCRIPTION,
        "price": "4680",
        "compareAt": "5280",
        "cost": "2860",
        "taxable": True,
        "optionName": "軸體",
        "optionValues": "Dawn 線性軸, Moss 段落軸",
        "dawnSku": "MFW75-WN-DN",
        "dawnStock": "36",
        "mossSku": "MFW75-WN-MS",
        "mossStock": "24",
        "seoTitle": "Miraform W75 胡桃木三模機械鍵盤｜75% 熱插拔",
        "seoDescription": "CNC 黑胡桃木外殼、三模連線、Gasket 結構與無刻 PBT 鍵帽。W75 支援熱插拔及 Windows、macOS、Linux。",
        "handle": "miraform-w75-walnut-mechanical-keyboard",
        "status": "啟用",
        "channel": ["網路商店"],
        "vendor": "Miraform",
        "category": CATEGORY_PATH,
        "tags": "胡桃木鍵盤, 三模鍵盤, 75% 鍵盤, 熱插拔, 無刻鍵帽, 桌面選物",
        "weight": "1.18",
        "origin": ORIGIN,
        "hs": "847160",
        "student": STUDENT,
    },
    "procurement": {
        "student": STUDENT,
        "manufacturer": "Miraform",
        "productName": "W75 胡桃木三模熱插拔機械鍵盤",
        "model": "MF-W75",
        "mpn": "MF-W75-WN",
        "gtin": "未申請",
        "category": CATEGORY_PATH,
        "origin": ORIGIN,
        "hs": "847160",
        "layout": "75% ANSI，84 鍵",
        "caseMaterial": "CNC 美國黑胡桃木外殼，植物性硬蠟油塗裝",
        "connection": "2.4 GHz／Bluetooth 5.3／USB-C 有線",
        "battery": "4,000 mAh 鋰聚合物電池",
        "dimensions": "323 × 136 × 38 mm",
        "netWeight": "1.18 kg",
        "compatibility": "Windows 11、macOS 13 以上、主流 Linux 發行版",
        "warranty": "18 個月",
        "bomMaterial0": "CNC 美國黑胡桃木外殼",
        "bomQty0": "1",
        "bomNote0": "植物性硬蠟油霧面塗裝",
        "bomMaterial1": "陽極鋁合金內骨架",
        "bomQty1": "1",
        "bomNote1": "霧黑",
        "bomMaterial2": "FR-4 熱插拔 PCB",
        "bomQty2": "1",
        "bomNote2": "南向軸座、NKRO",
        "bomMaterial3": "聚碳酸酯定位板",
        "bomQty3": "1",
        "bomNote3": "1.5 mm",
        "bomMaterial4": "PORON 夾心棉、IXPE 軸下墊、天然軟木底墊",
        "bomQty4": "各 1",
        "bomNote4": "PORON 於定位板與 PCB 之間；IXPE 0.5 mm；軟木 1.5 mm",
        "bomMaterial5": "4,000 mAh 鋰聚合物電池",
        "bomQty5": "1",
        "bomNote5": "內建",
        "moq": "12 把",
        "price12": "NT$3,650",
        "price48": "NT$3,420",
        "leadStock": "確認訂單後 7 個工作天",
        "leadBackorder": "確認訂單後 30 個工作天",
        "payment": "首批訂單 30% 訂金，出貨前付清餘款",
        "carton": "每箱 6 把；外箱 42 × 41 × 24 cm；毛重約 10.6 kg",
        "shippingWeight": "1.65 kg",
        "packageDimensions": "39.5 × 19.5 × 7.2 cm",
        "packageContents": "\n".join(PACKAGE_CONTENTS),
        "declaration": list(DECLARATIONS),
    },
}


def _s(fields: dict[str, FieldValue], name: str) -> str:
    value = fields[name]
    if not isinstance(value, str):
        raise TypeError(f"{name} is not a text field")
    return value


def _market_payload(f: dict[str, FieldValue]) -> dict[str, Any]:
    return {
        "category": _s(f, "category"),
        "title": _s(f, "title"),
        "brand": _s(f, "brand"),
        "model": _s(f, "model"),
        "condition": _s(f, "condition"),
        "variants": [
            {"option": "Dawn 線性軸", "sku": _s(f, "dawnSku"), "price": _s(f, "dawnPrice"), "stock": _s(f, "dawnStock")},
            {"option": "Moss 段落軸", "sku": _s(f, "mossSku"), "price": _s(f, "mossPrice"), "stock": _s(f, "mossStock")},
        ],
        "origin": _s(f, "origin"),
        "warrantyMonths": _s(f, "warranty"),
        "shippingWeightKg": _s(f, "weight"),
        "packageCm": {"length": _s(f, "length"), "width": _s(f, "width"), "height": _s(f, "height")},
        "highlights": _s(f, "highlights"),
        "imageOrder": list(ASSET_ORDER),
    }


def _studio_payload(f: dict[str, FieldValue]) -> dict[str, Any]:
    return {
        "title": _s(f, "title"),
        "description": _s(f, "description"),
        "mediaOrder": list(ASSET_ORDER),
        "category": _s(f, "category"),
        "vendor": _s(f, "vendor"),
        "tags": _s(f, "tags"),
        "pricing": {
            "price": _s(f, "price"),
            "compareAt": _s(f, "compareAt"),
            "cost": _s(f, "cost"),
            "taxable": f["taxable"] is True,
        },
        "optionName": _s(f, "optionName"),
        "optionValues": _s(f, "optionValues"),
        "variants": [
            {"sku": _s(f, "dawnSku"), "stock": _s(f, "dawnStock")},
            {"sku": _s(f, "mossSku"), "stock": _s(f, "mossStock")},
        ],
        "shipping": {
            "physical": True,
            "weight": _s(f, "weight"),
            "unit": "kg",
            "origin": _s(f, "origin"),
            "hsCode": _s(f, "hs"),
        },
        "seo": {"title": _s(f, "seoTitle"), "description": _s(f, "seoDescription"), "handle": _s(f, "handle")},
        "status": _s(f, "status"),
        "salesChannels": list(f["channel"]) if isinstance(f["channel"], list) else [],
    }


def _procurement_payload(f: dict[str, FieldValue]) -> dict[str, Any]:
    return {
        "identity": {
            "manufacturer": _s(f, "manufacturer"),
            "productName": _s(f, "productName"),
            "model": _s(f, "model"),
            "mpn": _s(f, "mpn"),
            "gtin": _s(f, "gtin"),
            "category": _s(f, "category"),
            "origin": _s(f, "origin"),
            "hsCode": _s(f, "hs"),
        },
        "specs": {key: _s(f, key) for key in ("layout", "caseMaterial", "connection", "battery", "dimensions", "netWeight", "compatibility", "warranty")},
        "bom": [
            {"section": section, "material": _s(f, f"bomMaterial{i}"), "quantity": _s(f, f"bomQty{i}"), "note": _s(f, f"bomNote{i}")}
            for i, section in enumerate(BOM_SECTIONS)
        ],
        "supply": {key: _s(f, key) for key in ("moq", "price12", "price48", "leadStock", "leadBackorder", "payment", "carton")},
        "logistics": {key: _s(f, key) for key in ("shippingWeight", "packageDimensions", "packageContents")},
        "declarations": list(f["declaration"]) if isinstance(f["declaration"], list) else [],
        "attachments": list(ASSET_ORDER),
    }


EXPECTED: dict[str, dict[str, Any]] = {
    "market": _market_payload(FIELDS["market"]),
    "studio": _studio_payload(FIELDS["studio"]),
    "procurement": _procurement_payload(FIELDS["procurement"]),
}
