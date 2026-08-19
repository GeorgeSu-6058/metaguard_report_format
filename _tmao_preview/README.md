# TMAO 版面預覽產生器

把 `index.js` 裡 TMAO 相關元件的輸出，重建成可以用瀏覽器看的 HTML。
**不是實機輸出** —— 報告引擎需要 Zope + LIMS 資料才能跑，這裡是用相同的 DOM 結構
與專案原始的 `index.css` 手動重建。

## 用法

```
python build.py         # 版面預覽：4 張 A4 頁
python build_full.py    # 全版報告結構：頁面順序與五套組對照
```

從任何目錄執行都可以，輸出會產生在這個資料夾裡：

- `tmao-layout-preview.html`
- `tmao-full-report-structure.html`

需要 Python 3，無第三方套件。Windows 終端若出現編碼錯誤，加上 `PYTHONIOENCODING=utf-8`。

## 想預覽不同風險等級

改 `../index.js` 裡的 `TMAO_MOCK_VALUE`，再重跑 `build.py`：

| 值 | 等級 |
|---|---|
| `4.5` | 低風險 |
| `7.8` | 中風險（目前設定） |
| `13.2` | 高風險 |

## 忠實度

`build.py` 的文字內容**全部從 `../index.js` 直接抽取**，不是複製貼上的副本：

- 章節標題、副標、非空腹警示 → `field_after()`
- 兩段敘述 → `contents_after()`，段落數不符會中止建置
- 建議文案 → `cdr()`，從 `CDR["zh-TW"]["TMAO"]` 讀取
- 醫師圖示 → bundle 內的 `DOCTOR_PNG`
- 樣式 → `../index.css` 原檔內嵌

因此改了程式再重跑，預覽就會跟著更新；抽取失敗會直接失敗而不是靜默產生過期內容。

幾何部分（分級門檻、色帶寬度、指標位置）是**照著程式重寫一遍**而非抽取，
所以改了 `Cutoff[ModelKeywords.TMAO]` 或 `TMAOBandWidths` 之後，
`build.py` 頂部的 `CUT` / `BANDS` / `RANGES` 也要一起改，否則預覽會與實際不符。

## 檔案

| 檔案 | 用途 |
|---|---|
| `build.py` | 版面預覽產生器 |
| `build_full.py` | 全版結構產生器（頁面順序表是人工整理的，改章節結構後需同步） |
| `tmpl.html` | 版面預覽的外框模板 |
