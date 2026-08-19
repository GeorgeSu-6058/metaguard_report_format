# TMAO 章節 — 進度與交接

> 最後更新：2026-08-19
> 分支：`feat/tmao-profile`（自 `main` 分出，**尚未 push**）
> HEAD：`154331f`

---

## 一句話現況

TMAO 章節（風險分級＋建議文案）**程式已完成、文案已通過審閱**，
但資料是假的（mock），且**從未在真實報告引擎上跑過**。

---

## 一、已完成

| 項目 | 狀態 |
|---|---|
| TMAO 章節頁（風險條＋敘述） | ✅ |
| 三級分級與門檻 | ✅ 0-6.2 / 6.3-9.9 / ≥10.0 μM |
| 切點出處與判讀限制 | ✅ 已寫入報告文案 |
| 中英文建議文案 | ✅ 已通過臨床審閱與修訂 |
| TMAO 專用建議頁 | ✅ `InterpretationTMAO02` |
| 總覽頁風險卡片 | ✅ |
| 非空腹樣本警示 | ✅ |
| 三個層級（MetaCardio / 獨立套組 / 既有套組） | ✅ 共用同一份程式碼 |
| 設定與驗證文件 | ✅ `MetaTMAO_LIMS_設定說明.md` |

## 二、未完成（依重要性）

1. **實機驗證** —— 從未在瀏覽器實際渲染過。
   語法（`node --check`）、分級邊界、CSS class 存在性都驗證過，但**版面、分頁、換行未經實測**。
   驗證步驟見 `MetaTMAO_LIMS_設定說明.md` 第四節（7 步）。
2. **TMAO 專屬 icon** —— `IconTitle` 的 `iconMap` 暫時把 `ModelKeywords.TMAO` 指向 `"ami"` 圖示，
   避免 `SvgIcon` 收到 `undefined`。需補一組 `tmao` / `tmao-circle` SVG 後改回。
3. **接真實資料** —— LIMS 尚未建立 `MetaboTMAO` Analysis Service。作法見設定說明第二節。
4. **部署** —— ⚠️ 見下方「部署落差」，這個問題**與 TMAO 無關但會擋住驗證**。
5. **英文報告排版未驗證** —— 英文字數比中文多約四成，建議卡片有換頁邏輯。
6. **無趨勢圖與歷史比較** —— 依「先做版面」的範圍決定，非遺漏。
   `SummaryTrend` 的 `notEmptyModels` 未納入 TMAO；章節元件已寫好條件渲染，有資料時會自動出現。
7. **相對風險倍數未提供** —— `relativeRisk` 為 `undefined`，風險條會自動隱藏該欄位。

---

## 三、關鍵決策紀錄

按時間排列。**這些都是問過並確認的，不要自行推翻。**

| 日期 | 決策 | 理由 |
|---|---|---|
| 08-17 | 走**通用三級**路線，不複製 AMI 的四級架構 | AMI 是全報告唯一四級疾病，有專屬 12 色指數條與顯示名稱重映射，全是特例 |
| 08-17 | 先做版面，資料用 mock | LIMS 端尚無 TMAO 檢測項目 |
| 08-18 | 切點出處：Cleveland HeartLab / Tang et al. (NEJM 2013) | 原本文案宣稱「依臨床文獻建議」卻無出處，已改為明確引用 |
| 08-18 | 判讀限制寫入報告 | 非診斷標準、須併同 eGFR 與近期飲食、須空腹採檢 |
| 08-18 | 移除白藜蘆醇與 DMB 的敘述（三處） | 證據以動物與體外為主，且文案前後語氣不一致 |
| 08-18 | 紅肉頻率改軟性表述 | 「每週不超過兩次」無營養準則背書 |
| 08-18 | 高風險補充劑措辭由指令改轉介 | 避免報告直接要求受檢者停用補充劑 |
| 08-18 | 低風險不出建議卡片 | 與 AD／CKD／FLD／T2D 一致 |
| 08-18 | 非空腹只顯示警示，不改切點 | 沒有非空腹的切點數據可用 |
| 08-18 | **分級改為 6.2 歸低風險**，中風險自 6.3 起算 | 規格修訂。連帶刪除自訂的 `computeTMAOLevelInfo()`，改用通用 `computeLevelInfo()` |
| 08-18 | 免疫章節 gate 不加 `!isMetaTMAO` | TMAO-only 樣本不會有免疫資料 |
| 08-19 | **TMAO 獨立於 MetaPro 之外**，可與 MetaCardio 同套組或自成套組 | 產品需求 |
| 08-19 | 為此新增 `InterpretationTMAO02` 專用建議頁，不重構 `FirstPage` | 重構會讓 TMAO-only 報告的年齡表格顯示 `-`，並連帶改變 CVA／AMI 在 MetaCardio 的既有輸出 |
| 08-19 | `showTMAO` 不做套組白名單 | 範圍由 LIMS 端「哪個套組勾選 `MetaboTMAO` 服務」控制，避免「有資料卻不顯示」 |

---

## 四、Commit 清單

```
154331f  feat(TMAO): give TMAO its own advice page so the copy ships without MetaPro
314a0cf  docs(TMAO): record that advice cards only ship in MetaPro, and why that is accepted
8fd89d1  feat(TMAO)!: move 6.2 into the low band per the revised tier spec
2f58212  style(TMAO): label the low band as a range, matching the overview card
21d4d6e  copy(TMAO): soften the high-tier supplement advice from an instruction to a referral
16f40b7  copy(TMAO): drop the resveratrol/DMB claim and soften the red-meat frequency
ba5241d  feat(TMAO): flag non-fasting samples beside the risk bar
f7fffc3  docs(TMAO): cite the actual cutpoint source and state the interpretation limits
e7932f3  feat(TMAO): add the trimethylamine N-oxide chapter as a generic three-tier disease
```

⚠️ **尚未 push。** 目前只存在於這台機器。要保險請執行：

```
git -c safe.directory="$PWD" push -u origin feat/tmao-profile
```

---

## 五、程式碼地圖

所有改動都在 `index.js`（手改 bundle，無原始碼專案 —— 見下方「陷阱」）。

| 構件 | 用途 |
|---|---|
| `ModelKeywords.TMAO = "MetaboTMAO"` | LIMS 資料鍵 |
| `MetaTMAOProfile` / `isMetaTMAO()` | 獨立套組判別 |
| `showTMAO(profiles)` | 章節顯示總開關（`!isMetaAge`） |
| `Cutoff[ModelKeywords.TMAO] = [6.2, 9.9]` | 分級門檻 |
| `computeLevelInfo()` | 分級（通用函式，非自訂） |
| `TMAORiskIndex` | 章節頁風險條 |
| `computeTMAOBarPosition()` / `TMAOBandWidths` / `TMAODisplayMax` | 風險條幾何 |
| `SummaryTMAORisk` | 總覽頁卡片風險條 |
| `InterpretationTMAO01` | 章節頁 |
| `InterpretationTMAO02` | TMAO 專用建議頁 |
| `firstPageWillRender()` | 防止與 `FirstPage` 重複出現 |
| `isNonFastingSample()` | 非空腹警示判斷 |
| `buildTMAOMockData()` / `TMAO_MOCK_ENABLED` / `TMAO_MOCK_VALUE` | 假資料 |
| `CDR["zh-TW"]["TMAO"]` / `CDR["en-US"]["TMAO"]` | 建議文案 |

用 `grep -n "TMAO" index.js` 可快速定位全部。

### 相關文件

- `MetaTMAO_LIMS_設定說明.md` —— LIMS 建檔、佈署、驗證步驟、已知待辦
- `_tmao_preview/` —— 產生版面預覽用的腳本（見第七節）

---

## 六、怎麼繼續

### 想看目前長什麼樣

```
cd _tmao_preview && python build.py && python build_full.py
```
產生 `tmao-layout-preview.html` 與 `tmao-full-report-structure.html`，用瀏覽器開。

### 想預覽其他風險等級

改 `index.js` 裡的 `TMAO_MOCK_VALUE`：`4.5` 低風險、`7.8` 中風險、`13.2` 高風險，再重跑上面的指令。

### 想接真實資料

見 `MetaTMAO_LIMS_設定說明.md` 第二節。重點：LIMS 建立 Keyword 為 `MetaboTMAO` 的
Analysis Service，然後把 `TMAO_MOCK_ENABLED` 改成 `false` 並補上真實的 model 分派分支。

### 想改文案

`CDR["zh-TW"]["TMAO"]` 與 `CDR["en-US"]["TMAO"]`，兩邊結構必須鏡像。
⚠️ 記得檔案裡中文可能以 `\uXXXX` 形式儲存，見下方陷阱。

---

## 七、陷阱（踩過的，別再踩）

1. **沒有原始碼專案。** 這個 repo 追蹤的是 build 產物。原專案 `homnia-tw`（TypeScript + Vite +
   pnpm monorepo）在原廠 MPROBE 手上，本機沒有、也沒有 sourcemap。
   **既定作法就是直接手改 `index.js`**，歷史上 20+ 個 commit 都是這樣做的，不是權宜之計。

2. **檔案裡中文是混合形式。** 有些區段是 `\uXXXX` escape，有些是原生 UTF-8。
   用 plain-text grep 搜中文會得到**假的 0 結果**。要搜尋請先解碼，或改用 ASCII 識別字定位。

3. **檔案是 CRLF。** 用腳本改檔時 anchor 要用對應行尾，寫回時 `newline="\r\n"`，
   否則整檔行尾會被改掉，diff 會爆炸。

4. **沒有 Tailwind build。** 用了 `index.css` 裡不存在的 class 會**靜默無樣式**。
   新增樣式只能用既有 class，或連 CSS 一起手改。
   目前 TMAO 四個元件共 69 個 class，全部確認存在。

5. **沒有 lint / 測試 / 型別檢查。** 唯一的把關是 `node --check index.js`（只驗語法）。
   邏輯正確性請自行寫小腳本模擬驗證，本次的分級邊界與防重複都是這樣驗的。

6. **部署落差（與 TMAO 無關，但會擋住驗證）：**
   bundle 在檔案系統裡有三份 ——
   - `index.js`（repo 根，真實來源，最新）
   - `…/bitbucket/senaite.impress-2.5.0/…/cdn/reports/meta-guard-tw/2.0.0/index.js`（較舊）
   - `…/buildout-cache/eggs/cp27mu/…egg/…/meta-guard-tw/`（**Zope 依 buildout.cfg 實際載入的是這份，是 2024/04 舊版**）

   改對了程式卻看不到效果，最常見原因就是改到沒被載入的那一份。

7. **四個套件別共用同一支 `index.js`。** 任何改動都要對 MetaAge / MetaGuard / MetaPro /
   MetaCardio 做回歸驗證。

---

## 八、線上文件

這三份是給人看的整理，內容都由腳本從 `index.js` 直接抽取，非手工謄寫：

- 文案審閱稿：https://claude.ai/code/artifact/3664d114-170b-4c63-9ab8-25c4ec669e7e
- 版面預覽（4 張 A4 頁）：https://claude.ai/code/artifact/8841f6d1-1efe-4bdf-b296-5fabc2374d28
- 全版報告結構：https://claude.ai/code/artifact/60979726-a1d8-455c-b0a9-6f0a2fe58a1f

> 預設私密。要給臨床審閱者看的話，用頁面上的分享選單。
