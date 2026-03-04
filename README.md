# NutriTag｜台灣營養標示計算工具

NutriTag 是一個使用 **Streamlit** 開發的網頁工具，

用於依據台灣食品標示相關法規，

協助進行 **食品配方營養成分試算與營養標示規劃**。

本工具適合應用於：

- 食品研發與配方設計
- 營養標示初步試算
- 包裝標示規劃與版面配置參考

## 🔧 功能特色

- ✅ 依「食品分類 / 原料名稱」搜尋營養成分資料
- ✅ 支援搜尋與分頁瀏覽，適合大量資料查找
- ✅ 可將多項原料加入配方並設定比例（總和需為 100%）
- ✅ 自動加權計算每 100 公克營養成分
- ✅ 依每份量與包裝份數換算營養標示
- ✅ 可選擇是否顯示每日參考值（DV%）
- ✅ 即時產生三欄式營養標示 HTML
- ✅ 支援多種標籤尺寸，可直接列印或轉 PDF

---

## 📁 專案結構

```
NutriTag/
├─ app.py # 主程式（Streamlit App）
├─ selected_columns.csv # 原料營養成分資料庫
├─ preprocess_nutritag_data.py # （選用）資料前處理腳本
├─ requirements.txt # Python 套件需求
└─ README.md
```

## 🚀 快速開始

1. **安裝環境**

   ```bash
   python -m venv .venv          # 建議使用虛擬環境
   source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt

   # Windows:
   # .venv\Scripts\activate
   ```
1. **安裝套件**

```bash
pip install -r requirements.txt
```

3. **準備資料**\
   將營養成分資料存成 `selected_columns.csv`，欄位需包含：

   - `食品分類`
   - `樣品名稱`
   - `粗蛋白(g)`、`粗脂肪(g)`、`飽和脂肪(g)`、`總碳水化合物(g)`、`糖質總量(g)`、`鈉(mg)`、`反式脂肪(mg)`、`酒精含量(g)` 等數值欄位
4. **應用程式**

```bash
streamlit run app.py
```

在瀏覽器中開啟提示的 URL（通常是 `http://localhost:8501`）。

## 📊 使用流程說明

於左側 Sidebar 選擇「食品分類」或輸入原料關鍵字

透過分頁瀏覽或搜尋，將原料加入配方

設定各原料比例（總和需為 100%）

輸入每一份量與本包裝含量

即時預覽營養標示，並下載 HTML 檔案

## 🛠 功能說明

- 從 CSV 資料庫篩選食品分類及樣品名稱
- 將多種原料加入配方並設定比例（比例總和需等於 100%）
- 輸入每一份量與本包裝份數
- 顯示營養標示結果，可選擇是否顯示每日參考值（DV%）
- 產生三欄式 HTML 格式的營養標示，方便複製到網頁或報表中

## 🧹 資料預處理

`preprocess_nutritag_data.py` 提供一些範例程式，可用來從原始資料檔案過濾、清理並產生 `selected_columns.csv`。

```bash
python preprocess_nutritag_data.py
```

(視腳本內容而定，請自行調整欄位與路徑)

## 📦 依賴

- Python 3.8+
- streamlit
- pandas

## 📝 注意事項

- 請確保 `selected_columns.csv` 放在與 `app.py` 相同的目錄中。
- 若找不到資料檔案，應用會顯示錯誤並停止。
- 成分比例需設定為數值且總和為 100% 才會顯示正確結果。

## 💡 擴充想法

- 支援上傳 CSV 檔案、或從資料庫查詢
- 新增更多營養成分欄位
- 匯出 PDF/圖片格式的標示
- 配合包裝設計建立可列印的排版

## 📘 資料來源與免責聲明

資料來源：

本工具使用之原料營養成分資料，主要參考自：

衛生福利部食品藥物管理署（TFDA）

食品營養成分資料庫（新版）

https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178

免責聲明：

本工具僅作為食品研發、配方試算與營養標示規劃之輔助用途。

實際產品營養標示數值，

仍應以實際檢驗結果為準，

並依「包裝食品營養標示應遵行事項」及相關法規進行最終確認。

---

此專案為個人/內部工具，歡迎自由修改與貢獻。