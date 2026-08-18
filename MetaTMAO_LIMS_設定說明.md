# 氧化三甲胺（TMAO）章節 — LIMS 建檔與佈署說明

> 本文件說明 **氧化三甲胺（Trimethylamine N-oxide, TMAO）** 章節如何加入 `meta-guard-tw` 報告引擎，
> 以及後續 LIMS 端需要做哪些設定才能接上真實檢測資料。
>
> ⚠️ **目前狀態：版面已完成，資料為假資料（mock）。** LIMS 端尚未建立 `MetaboTMAO` 這個 Analysis Service，
> 報告中顯示的 TMAO 濃度來自程式內建常數，**尚不可用於出具正式報告**。

---

## 一、這次改了什麼（程式碼，已完成）

TMAO 以**通用三級疾病**的形式加入引擎，可同時出現在三種層級：

| 層級 | 條件 | 說明 |
|---|---|---|
| MetaCardio 內的章節 | `HOMNIATW-MetaCardio-…` | 與 CVA、AMI 並列，章節編號 2.3 |
| 獨立套組（新 Profile） | `HOMNIATW-MetaTMAO-…` | 只出 TMAO 一章，章節編號 2.1，其餘疾病章節全部關閉 |
| 既有套組的一個項目 | MetaGuard / MetaPro | 排在 AMI 之後，章節編號 2.6 |

三個層級**共用同一份程式碼**，不是三套實作。顯示條件統一為 `showTMAO(profiles) = !isMetaAge(profiles)`。

### 新增的程式構件

- 資料鍵 `ModelKeywords.TMAO = "MetaboTMAO"`，並登記進 `ReportModelKeywords`、`diseaseData`、`modelInfoData`、`getHistorySample` 的歷史容器。
- Profile 常數 `MetaTMAOProfile = "MetaTMAO"` 與判別函式 `isMetaTMAO()`。
- 分級門檻 `Cutoff[ModelKeywords.TMAO] = [6.2, 9.9]`，分級沿用引擎通用的 `computeLevelInfo()`。
- 章節元件 `InterpretationTMAO01`、建議頁 `InterpretationTMAO02`、風險條 `TMAORiskIndex`、總覽卡片 `SummaryTMAORisk`。
- 非空腹判斷 `isNonFastingSample()`、防重複判斷 `firstPageWillRender()`。
- 中英文建議文案 `CDR["zh-TW"]["TMAO"]` / `CDR["en-US"]["TMAO"]`（各含 Moderate / High 兩級）。
- 假資料產生器 `buildTMAOMockData()`，由 `TMAO_MOCK_ENABLED` 開關控制。

### 風險分級

| 等級 | 濃度範圍 | 判定 | 報告標籤 |
|---|---|---|---|
| 低風險 | 0 – 6.2 μM | `value <= cutoff[0]` | `0-6.2` |
| 中風險 | 6.3 – 9.9 μM | `cutoff[0] < value <= cutoff[1]` | `6.3-9.9` |
| 高風險 | ≥ 10.0 μM | `value > cutoff[1]` | `≥10.0` |

門檻存為 `Cutoff[ModelKeywords.TMAO] = [6.2, 9.9]`；標籤由門檻推導（低帶上界、+0.1 起算中帶、中帶上界 +0.1 起算高帶），章節風險條與總覽卡片共用同一組推導，不會各自寫死。

### 切點出處

風險分層採用 **Cleveland HeartLab** 臨床檢測之判讀切點：

- **6.2 μM** — 源自 Tang 等人發表於《新英格蘭醫學期刊》（*N Engl J Med*, 2013）之研究，
  為 4,007 位接受選擇性冠狀動脈攝影受檢者中**最高風險四分位**之切點。
- **≥ 10.0 μM** — 對應 Cleveland HeartLab **參考族群 95% 區間之上限**。

### 判讀限制（已寫入報告文案）

- 本分層為心血管風險之**輔助評估參考，非疾病診斷標準**。
- 判讀須併同**腎功能（eGFR）**評估 —— TMAO 主要經腎臟清除，腎功能不全會造成濃度蓄積。
- 判讀須併同**近期飲食狀況**（深海魚、紅肉、蛋、含左旋肉鹼補充品）。
- **本檢測須於空腹狀態採檢。**

> 📌 邊界語意：6.2 μM 屬**低風險**，中風險自 6.3 起算。這正好是引擎通用函式
> `computeLevelInfo()` 的 `<=` 邊界行為，因此 TMAO 直接沿用，沒有自訂分級函式。
>
> （早期版本規格為「低風險 < 6.2、中風險自 6.2 起算」，當時為此寫了 `computeTMAOLevelInfo()`
> 採嚴格小於邊界。規格於 2026-08-18 改為 6.2 歸低風險後，該函式已移除。
> 若日後門檻語意再變動，請優先確認能否沿用 `computeLevelInfo()`，避免又長出一個平行函式。）

### 為什麼不沿用 AMI 的做法

AMI 是全報告唯一的**四級**疾病（多一個「風險升高 / Increased」），並帶有 12 色指數條、
以及一組「後端『中風險』→ 前端顯示『風險略升』」的顯示名稱重映射。這些都是 AMI 專屬邏輯。
TMAO 為三級，**刻意不繼承**上述任何一項，改走與 AD / CKD / FLD / T2D 相同的通用路線。

### 為什麼風險條是另寫的

引擎通用的 `SummaryRisk` / `DiseaseRiskIndex` 以 `dynamicCutoff()` 計算位置，座標系寫死為百分比（0–100），
並在數值後固定加上 `%`。TMAO 的單位是 μM（典型範圍 0–20），套用會導致指標位置錯誤且單位顯示錯誤。
因此另寫 `TMAORiskIndex` / `SummaryTMAORisk`，採固定三等分色帶與分段線性對應
（6.2 μM 落在 33.3%、10 μM 落在 66.6%，超過 `TMAODisplayMax = 20` 則貼齊右端）。

## 二、假資料（目前）與如何接上真實資料

假資料注入點在 `formatLimsData()` 的 `analysesModelData.forEach(...)` 迴圈**之後**：

```js
if (!diseaseData[ModelKeywords.TMAO] && TMAO_MOCK_ENABLED) {
  diseaseData[ModelKeywords.TMAO] = buildTMAOMockData({
    cutoff: Cutoff[ModelKeywords.TMAO]
  });
}
```

目前假資料為 **`TMAO_MOCK_VALUE = 7.8` μM（中風險）**。要預覽其他等級，改這個常數即可
（例如 `4.5` 看低風險、`13.2` 看高風險）。

**接上真實資料時：**

1. 在 LIMS 建立 Analysis Service，**Keyword 必須為 `MetaboTMAO`**。
2. 確認後端回傳的資料結構含 `index.value`（μM 濃度數值）。
3. 將 `TMAO_MOCK_ENABLED` 改為 `false`，並在 `formatLimsData()` 的 model 分派 if-else 鏈中，
   為 `ModelKeywords.TMAO` 補上真實分支（可參考同檔的一般疾病分支寫法）。
4. 上述判斷式寫成 `!diseaseData[...] && TMAO_MOCK_ENABLED`，因此真實分支一旦填入資料，
   假資料就不會覆蓋它 —— 兩者可安全並存，便於分階段切換。

## 三、在 LIMS 建立 MetaTMAO 套組（**需手動操作**，僅獨立套組層級需要）

若只是讓 TMAO 出現在既有的 MetaCardio / MetaGuard / MetaPro 報告中，**不需要**這一節。
只有要做成獨立套組時才需要：

1. 以 **Lab Manager** 登入 LIMS。
2. **Setup → Analysis Profiles → Add**。
3. 填寫：
   - **Title**：`MetaTMAO`
   - **Profile Keyword / `profile_key`**：`HOMNIATW-MetaTMAO-<代碼>`
     - ⚠️ **第二段必須正好是 `MetaTMAO`**（大小寫相符）。
     - 前綴維持 `HOMNIATW`，才會載入 `meta-guard-tw` 報告 bundle。
   - **Services**：只勾選 TMAO（資料鍵 `MetaboTMAO`）。
4. 儲存。

> ⚠️ **採檢需空腹。** 建檔時請於 Analysis Service 的採檢說明註明空腹要求。

### 非空腹樣本的處理

當 Sample 的 Sampling Deviation 為 `Non-Fasting` 時，TMAO 章節的風險條下方會加註一行警示：

> ※ 本次為非空腹採檢，結果僅供參考。

實作為 `isNonFastingSample(deviation)`，判斷條件是 `deviation === "Non-Fasting"`
（`deviation` 來自 LIMS 的 `getSamplingDeviationTitle`，全報告只有 `Fasting` / `Non-Fasting` 兩種值）。

**注意這只是顯示警示，不改變判讀：**`Cutoff[ModelKeywords.TMAO]` 仍是單一陣列，
非空腹樣本套用的是**同一組切點**。由於 TMAO 濃度本身會受近期飲食影響，
非空腹樣本的結果可能系統性偏高，警示的用途是提醒判讀者，而非校正數值。

若日後要讓非空腹樣本改用另一組切點，需將 `Cutoff[ModelKeywords.TMAO]` 改寫為
`{ Fasting: [...], NonFasting: [...] }` 形式（參考 `Cutoff[ModelKeywords.T2D]`），
並改用 `getCutoff()` 取值 —— 但目前**沒有非空腹的切點數據**。

警示只出現在章節頁的風險條下方，總覽頁的 TMAO 卡片不加註（該卡片高度固定 84px，塞不下）。

## 四、驗證

1. **MetaCardio**：出一筆 MetaCardio 報告，確認章節順序為 2.1 腦中風 → 2.2 急性心肌梗塞 → **2.3 氧化三甲胺**，
   且總覽頁出現 TMAO 風險卡片。
2. **MetaGuard / MetaPro**：確認 TMAO 排在急性心肌梗塞之後（2.6），且**其後章節編號已順移**——
   脂肪肝 2.7、糖尿病 2.8、腎臟病 2.9（原為 2.6 / 2.7 / 2.8）。
3. **MetaAge**：確認 TMAO **不出現**（`showTMAO` 對 MetaAge 回傳 false）。
4. **建議文案**：把 `TMAO_MOCK_VALUE` 依序設為 `4.5` / `7.8` / `13.2`，確認：
   - 4.5 → 低風險，健康管理建議頁**不出現** TMAO 卡片（低風險不列入異常清單，與其他疾病一致）。
   - 7.8 → 中風險，出現 Moderate 文案（無「尋求專業評估與干預」段落）。
   - 13.2 → 高風險，出現 High 文案（**含**「尋求專業評估與干預」段落）。
5. **建議頁不重複**：在 MetaPro 報告（有 Aging 資料）確認 TMAO 建議卡片**只出現一次**，
   且是在既有的綜合建議頁 `FirstPage` 上；在 MetaCardio 與 MetaTMAO 報告確認出現一張
   由 `InterpretationTMAO02` 產生的單一疾病建議頁。兩者不應同時出現。
6. **非空腹警示**：出一筆 Sampling Deviation 設為 `Non-Fasting` 的 Sample，確認風險條下方出現
   「※ 本次為非空腹採檢，結果僅供參考。」；再出一筆 `Fasting` 的，確認**不出現**該行。
7. **回歸**：另開 MetaAge / MetaGuard / MetaPro / MetaCardio 各一筆，確認四個既有套組除了新增的 TMAO 章節與編號順移外，
   其餘版面**完全不變**。

## 五、建議卡片的輸出範圍

TMAO 建議文案（`CDR["*"]["TMAO"]`）有**兩條輸出路徑**：

| 路徑 | 元件 | 何時輸出 |
|---|---|---|
| 既有的綜合建議頁 | `FirstPage` | `MetaboAging && !isMetaCardio && !isMetaTMAO && isMetaPro` |
| TMAO 專用建議頁 | `InterpretationTMAO02` | 上述條件**不**成立時，且 TMAO 為中／高風險 |

`InterpretationTMAO02` 內部以 `firstPageWillRender(profiles, MetaboAging)` 判斷 `FirstPage`
是否會出現；若會，就回傳 `null`，避免同一份報告出現兩張 TMAO 建議卡片。

實際結果（TMAO 為中／高風險時）：

| 套組 | TMAO 章節 | 建議卡片 | 由哪個元件輸出 |
|---|---|---|---|
| MetaAge | 無 | 無 | — |
| MetaGuard | 有（2.6） | 有 | `InterpretationTMAO02` |
| MetaPro | 有（2.6） | 有 | `FirstPage`（既有綜合頁） |
| MetaCardio | 有（2.3） | 有 | `InterpretationTMAO02` |
| MetaTMAO | 有（2.1） | 有 | `InterpretationTMAO02` |

低風險不輸出建議卡片（與 AD／CKD／FLD／T2D 一致）。

### 為什麼另開一頁而不是改 `FirstPage`

`FirstPage` 頂部固定有「生理年齡／實際年齡／老化速度」表格，資料來自 `MetaboAging`。
把它搬出 Aging fragment 獨立掛載，在沒有 Aging 資料的 TMAO-only 報告中那張表會顯示為 `-`，
且會連帶讓 CVA／AMI 的建議文案也出現在 MetaCardio（既有行為變更）。
因此改為新增一個只承載 TMAO 建議的精簡頁面，**既有四個套組的輸出完全不變**
（MetaPro 走原本的 `FirstPage`，`InterpretationTMAO02` 在該情況回傳 `null`）。

代價是報告中存在兩種建議頁型：MetaPro 是綜合多疾病的建議頁，其餘套組是單一疾病的精簡頁。

### 2026-08-18 其他確認事項

- **免疫章節的 gate 未加 `!isMetaTMAO`** —— 維持原樣。TMAO-only 樣本不會有免疫資料，不會誤觸發。
  ⚠️ latent：若日後在 MetaTMAO profile 加掛免疫檢測服務，免疫章節會出現在 TMAO-only 報告中。
- **`showTMAO` 不做套組白名單** —— 維持 `showTMAO = !isMetaAge`，靠 LIMS 端「哪個套組有勾選
  `MetaboTMAO` 服務」來控制範圍。這樣日後要把 TMAO 加進別的套組不需改程式，
  也避免「有資料卻不顯示」這種難以除錯的情況。
- **TMAO 不放進 MetaPro** —— 這是 LIMS 設定層的事，不需改程式：MetaPro 套組不勾選
  `MetaboTMAO` 服務即可。若哪天勾了，章節與建議卡片都會正常輸出（走 `FirstPage`）。

## 六、已知待辦

- **TMAO 專屬 icon 未製作**。`IconTitle` 的 `iconMap` 目前把 `ModelKeywords.TMAO` 暫時指向 `"ami"` 圖示，
  避免 `SvgIcon` 收到 `undefined`。需補一組 `tmao` / `tmao-circle` SVG 後改回。
- **總覽頁人形器官圖未標示 TMAO**。`getOrganSvgUrl()` 沒有對應部位（TMAO 屬腸道—血管軸，不對應單一器官），
  目前不點亮任何部位。
- **無趨勢圖與歷史比較**。`SummaryTrend` 的 `notEmptyModels` 未納入 TMAO，
  `index.lastTest` / `diffWithLastTest` 皆為 `undefined`（章節元件已寫好條件渲染，有資料時會自動出現）。
  這是依「先做版面、只要風險分級＋建議文案」的範圍決定，非遺漏。
- **相對風險倍數未提供**。`relativeRisk` 為 `undefined`，風險條會自動隱藏該欄位。
- **英文報告文案已備妥但未驗證**。`CDR["en-US"]["TMAO"]` 結構與中文鏡像一致，尚未實際出過英文報告確認排版。
