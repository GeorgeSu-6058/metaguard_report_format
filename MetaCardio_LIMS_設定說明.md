# MetaGuard Cardio（美塔力-心安）套組 — LIMS 建檔與佈署說明

> 品牌顯示名為 **MetaGuard Cardio / 美塔力-心安**（原 MetaCardio / 好心力-專業版）。
> ⚠️ LIMS 端 `profile_key` **仍為 `HOMNIATW-MetaCardio-…`**（第二段 `MetaCardio` 是偵測用鍵，不隨顯示名改變）。

> 本文件說明如何讓 **MetaCardio** 套組在（測試環境）SENAITE LIMS 平台出現為可勾選的套組，並正確套用只含 **腦中風（CVA）** 與 **急性心肌梗塞（AMI）** 的 MetaCardio 報告版面。

---

## 一、這次改了什麼（程式碼，已完成）

報告引擎（`meta-guard-tw` bundle）新增第四個套件別 **MetaCardio**，與 MetaAge / MetaGuard / MetaPro 共用同一支 `index.js`，依 `profile_key` 第二段字串分支。

- 新增 `MetaCardioProfile = "MetaCardio"` 常數與 `isMetaCardio()` 判別函式。
- 封面品牌：大標題兩行 `METAGUARD` / `CARDIO`、副標「MetaGuard Cardio 美塔力-心安」/ 酒紅主題（`#8A4639`→`#5F251A`）＋藍色側欄（沿用引擎既有藍條）。封面為漸層背景＋動態疊字，受檢者/檢驗日/報告日由病人資料自動帶入。
- 內容：**只顯示** 檢測結果總覽（器官圖只點亮心/腦）、腦中風、急性心肌梗塞、健康動態追蹤（只含 CVA/AMI）、檢測說明與參考文獻附錄、封底。
- CVA / AMI 做到 **MetaPro 深度**（含 heatmap、Sankey、詳細解讀頁），圖表初始化一併開啟。
- 其餘（生理年齡、免疫、阿茲海默、脂肪肝、糖尿病、腎臟病）一律隱藏；TOC 章節自動重編為 2.1 腦中風 / 2.2 急性心肌梗塞。

檔案：`index.js`、`index.css`（repo 根目錄）。

## 二、佈署（已完成）

已將更新後的 `index.js` / `index.css` 覆蓋到測試 LIMS 的報告 bundle：

```
home_LIMS_code/senaite/buildout-cache/bitbucket/senaite.impress-2.5.0/src/senaite/impress/browser/static/cdn/reports/meta-guard-tw/2.0.0/index.js
                                                                                                              .../index.css
```

> 若測試 LIMS 有快取，重新整理報告頁或清除瀏覽器快取即可載入新版。四個套件（MetaAge/MetaGuard/MetaPro/MetaCardio）共用此版；`mProbeReports.pt` 不需修改。

## 三、在 LIMS 建立 MetaCardio 套組（**需你手動操作**）

套組本身存於 LIMS 資料庫（ZODB），不是 repo 檔案，需在執行中的測試 LIMS 建立：

1. 以 **Lab Manager** 登入測試 LIMS。
2. 進入 **Setup（設定）→ Analysis Profiles（分析套組）→ Add（新增）**。
3. 填寫欄位：
   - **Title**：`MetaCardio`
   - **Profile Keyword / `profile_key`**：`HOMNIATW-MetaCardio-<代碼>`
     - ⚠️ **第二段必須正好是 `MetaCardio`**（大小寫相符），報告才會套用 MetaCardio 版面。
     - 前綴維持 `HOMNIATW`（與現有 MetaPro/MetaGuard 相同），才會載入 `meta-guard-tw` 報告 bundle。
     - 第三段（`<代碼>`）比照現有套組格式自訂即可（需全站唯一）。
   - **Services（分析服務）**：**只勾選兩個**——
     - 腦中風 **CVA**（資料鍵 `MetaboCVA`）
     - 急性心肌梗塞 **AMI**（資料鍵 `HeartCeramides`）
     - 即現有 MetaPro 套組裡「腦中風」「急性心肌梗塞」所用的同兩個 Analysis Service。**不要**加入生理年齡、免疫或其他疾病服務。
4. **儲存**（系統會驗證 `profile_key` 唯一性）。

## 四、驗證

1. 新建一筆 Sample / Analysis Request，套組選 **MetaCardio**，輸入（或匯入）CVA 與 AMI 結果。
2. 出報告，確認：
   - 封面為酒紅、大標題兩行 **METAGUARD / CARDIO**，副標「MetaGuard Cardio 美塔力-心安」，受檢者/檢驗日/報告日正確。
   - 內容只有：總覽（器官圖僅心、腦）→ 腦中風（含 heatmap/詳解）→ 急性心肌梗塞（含 heatmap/詳解）→ 健康動態追蹤（只列 CVA/AMI）→ 檢測說明、參考文獻附錄、封底。
   - **不出現** 生理年齡、免疫、阿茲海默、脂肪肝、糖尿病、腎臟病。
   - 目錄章節為 2.1 腦中風、2.2 急性心肌梗塞。
3. 回歸：另開 MetaPro / MetaGuard / MetaAge 各一筆，確認三個既有套組封面與版面**完全不變**。

## 五、封底（固定使用指定 PDF 最後一頁）

封底直接採用 `HOTW260410SRAC07_R01_猝死包套組 1.pdf` 的**最後一頁（第 28 頁）整頁圖**（深酒紅底＋世界地圖＋全球據點/地址/QR，已全部內嵌），設為 `MetaCardioBGImage`。此封底為**固定、不隨病人變動**。

因該圖已含所有地址與 QR，MetaCardio 時 `BackCover` 會**關閉引擎的動態疊字/QR 圖層**（`children: !isMetaCardio(...) && ...`），只鋪這張圖，避免內容重複。若日後要改封底，替換 `MetaCardioBGImage` 的圖即可。

## 六、其他小事項（非阻擋）

- 總覽器官圖為整張人體輪廓，未受檢器官以中性白色呈現（心、腦依實際風險上色），屬引擎既有行為。
