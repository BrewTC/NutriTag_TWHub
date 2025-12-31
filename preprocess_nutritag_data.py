import pandas as pd

# 必要的列轉換函數
def excel_col_to_index(col):
    col = col.upper()
    value = 0
    for ch in col:
        value = value * 26 + (ord(ch) - ord('A') + 1)
    return value - 1

# 定義需要的列
cols = ["B", "C", "E", "J", "K", "L", "N", "P", "W", "CK", "DF"]
indices = [excel_col_to_index(c) for c in cols]
print("對應索引欄位 =", indices)

# 讀取文件
df = pd.read_csv("營養標示平台.csv", encoding="utf-8")
selected_df = df.iloc[:, indices]

# 使用 UTF-8 BOM 編碼保存為 CSV
selected_df.to_csv("selected_columns.csv", index=False, encoding="utf-8-sig")
print("處理完成，已儲存為 selected_columns.csv")