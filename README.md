# NutriTag｜台灣營養標示計算工具

這是一個使用 **Streamlit** 建立的簡易網頁應用程式，用於根據台灣食品標示法規計算營養標示。
使用者可以從資料庫中挑選食品原料，設定各原料比例與每一份量，並即時產生營養標示 HTML。

## 📁 專案結構

```
NutriTag_TWHub/
├─ app.py                   # 主應用程式
├─ preprocess_nutritag_data.py  # (可選) 數據預處理腳本
├─ requirements.txt         # Python 依賴清單
└─ selected_columns.csv     # 包含食品營養成分的資料庫 (CSV)
```

## 🚀 快速開始

1. **安裝環境**

   ```bash
   python -m venv .venv          # 建議使用虛擬環境
   source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```

2. **準備資料**

   將營養成分資料存成 `selected_columns.csv`，欄位需包含：
   - `食品分類`
   - `樣品名稱`
   - `粗蛋白(g)`、`粗脂肪(g)`、`飽和脂肪(g)`、`總碳水化合物(g)`、`糖質總量(g)`、`鈉(mg)`、`反式脂肪(mg)`、`酒精含量(g)` 等數值欄位

3. **啟動應用程式**

   ```bash
   streamlit run app.py
   ```

   在瀏覽器中開啟提示的 URL（通常是 `http://localhost:8501`）。

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

---

此專案為個人/內部工具，歡迎自由修改與貢獻。