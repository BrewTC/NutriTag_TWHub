import streamlit as st
import pandas as pd
import os

# ==========================
# 配置及資料載入
# ==========================
st.set_page_config(
    page_title="NutriTag｜台灣營養標示計算工具",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 載入 CSV 資料
DATA_FILE = "selected_columns.csv"
# 為了避免你測試時沒有檔案報錯，這裡加個簡單的防呆，實際使用請確保檔案存在
if not os.path.exists(DATA_FILE):
    st.error(f"找不到檔案 `{DATA_FILE}`，請確認是否放在同一目錄內。")
    st.stop()

# 讀取 CSV，並確保資料完整性
df = pd.read_csv(DATA_FILE)

# 【新增這行】先把「食品分類」或「樣品名稱」是空的資料行刪除
# 這樣就不會讀到空行或無效資料
df.dropna(subset=["食品分類", "樣品名稱"], inplace=True)

df.fillna(0, inplace=True)  # 數值計算建議填補為 0 比較安全

# 可選資料欄位
FOOD_CATEGORIES = df["食品分類"].astype(str).drop_duplicates().sort_values().tolist()

# 數值型欄位清單 (CSV 原始欄位)
NUMERIC_FIELDS = ["粗蛋白(g)", "粗脂肪(g)", "飽和脂肪(g)", "總碳水化合物(g)", "糖質總量(g)", "鈉(mg)", "反式脂肪(mg)", "酒精含量(g)"]

# 台灣每日參考值 (Daily Values) - ⚠️ 這裡的 Key 改為英文，以便跟 HTML 產生器對應
DAILY_VALUES = {
    "calories": 2000.0,             # 熱量
    "protein": 60.0,                # 蛋白質
    "fat": 60.0,                    # 脂肪
    "saturatedFat": 18.0,           # 飽和脂肪
    "carbs": 300.0,                 # 碳水化合物
    "sodium": 2000.0,               # 鈉
    "transFat": None,               # 反式脂肪
    "sugar": None,                  # 糖
}

# ==========================
# 分步操作界面
# ==========================

st.title("NutriTag｜台灣營養標示計算工具")
st.caption("依據台灣食品標示法規，快速產生營養標示")
st.sidebar.header("篩選條件")

# ==========================
# 初始化 Session State
# ==========================
if "selected_items" not in st.session_state:
    # 確保包含所有欄位
    st.session_state.selected_items = pd.DataFrame(columns=df.columns.tolist() + ["比例(%)"])

st.sidebar.header("加入原料")

# --------------------------
# Step 1：選分類
# --------------------------
food_category = st.sidebar.selectbox(
    "選擇食品分類（僅用於篩選資料庫）",
    ["全部分類"] + FOOD_CATEGORIES
)

if food_category == "全部分類":
    browse_df = df.copy()
else:
    browse_df = df[df["食品分類"] == food_category]

# --------------------------
# Step 2：選樣品名稱並加入清單
# --------------------------
sample = st.sidebar.selectbox(
    "選擇樣品名稱",
    ["請選擇"] + browse_df["樣品名稱"].tolist()
)

if sample != "請選擇":
    sample_row = browse_df[browse_df["樣品名稱"] == sample].iloc[0]

    if st.sidebar.button("➕ 加入原料"):
        row = sample_row.copy()
        row["比例(%)"] = 0.0
        
        # 將 Series 轉為 DataFrame 並合併
        row_df = pd.DataFrame([row])
        st.session_state.selected_items = pd.concat(
            [st.session_state.selected_items, row_df],
            ignore_index=True
        )
        st.sidebar.success(f"已加入：{sample}")

# --------------------------
# 顯示目前「已選原料清單」
# --------------------------
st.markdown("### 已選原料清單（可跨食品分類加入）")

if st.session_state.selected_items.empty:
    st.info("尚未加入任何原料。")
else:
    # ===========================
    # 1. 比例編輯（移到最上方）
    # ===========================
    st.markdown("#### 請右滑編輯各原料比例（%）")

    edited_data = st.data_editor(
        st.session_state.selected_items,
        use_container_width=True,
        hide_index=True,
        key="selected_items_table",
        disabled=["食品分類", "樣品名稱"] + [c for c in df.columns if c != "比例(%)"],
        column_config={
            "比例(%)": st.column_config.NumberColumn(
                "比例 (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
            )
        },
    )

    # --- 比例加總檢核 ---
    total_ratio = edited_data["比例(%)"].sum()

    if abs(total_ratio - 100.0) > 0.05:
        st.warning("⚠️ 比例加總不等於 100%")
    else:
        st.success("✅ 比例加總為 100%")

    # total_ratio = edited_data["比例(%)"].sum()
    # col_msg_1, col_msg_2 = st.columns([1, 2])
    # # with col_msg_1:
    # #     st.metric("比例加總 (%)", f"{total_ratio:.1f}")
    # with col_msg_2:
    #     if abs(total_ratio - 100.0) > 0.05:
    #         st.warning("⚠️ 比例加總不等於 100%")
    #     else:
    #         st.success("✅ 比例加總為 100%")

    # --- 套用按鈕 (靠右) ---
    # 使用 columns 排版：[空白佔位, 按鈕區]
    col_space_1, col_btn_1 = st.columns([5, 1.5]) 
    with col_btn_1:
        if st.button("✔ 套用比例修改", use_container_width=True):
            st.session_state.selected_items = edited_data.copy()
            st.success("已套用") # 簡短提示即可

    st.markdown("---")

    # ===========================
    # 2. 刪除原料（移到下方）
    # ===========================
    st.markdown("#### （選填）刪除原料")
    
    # 使用 columns 排版：[空白佔位, 下拉選單區, 刪除按鈕區]
    # 稍微調整比例讓下拉選單寬一點，顯示名稱才不會被切掉
    # col_space_2, col_input_2, col_btn_2 = st.columns([3.5, 2.5, 1.5])
    col_input_2, col_btn_2 = st.columns([4, 1.5])
    
    with col_input_2:
        # 產生選項列表：格式為 "1. 樣品名稱", "2. 樣品名稱"...
        delete_options = [
            f"{i+1}. {row['樣品名稱']}" 
            for i, row in st.session_state.selected_items.iterrows()
        ]
        
        # 下拉選單
        selected_option = st.selectbox(
            "選擇要刪除的原料",
            options=delete_options,
            label_visibility="collapsed" # 隱藏標籤
        )
    
    with col_btn_2:
        if st.button("🗑 刪除此原料", type="primary", use_container_width=True):
            if selected_option:
                # 找出使用者選的是第幾個選項 (從 0 開始算，對應 DataFrame index)
                # 因為我們每次刪除都會 reset_index，所以選項順序剛好等於 DataFrame 索引
                idx_to_drop = delete_options.index(selected_option)
                
                st.session_state.selected_items = (
                    st.session_state.selected_items
                    .drop(st.session_state.selected_items.index[idx_to_drop])
                    .reset_index(drop=True)
                )
                st.rerun()
                
    # # ===========================
    # # 2. 刪除原料（移到下方）
    # # ===========================
    # st.markdown("#### 刪除原料")
    
    # # 使用 columns 排版：[空白佔位, 輸入行號區, 刪除按鈕區]
    # col_space_2, col_input_2, col_btn_2 = st.columns([4, 2, 1.5])
    
    # with col_input_2:
    #     delete_index = st.number_input(
    #         "刪除行號",
    #         min_value=0,
    #         max_value=len(st.session_state.selected_items) - 1,
    #         step=1,
    #         value=0,
    #         label_visibility="collapsed" # 隱藏標籤讓版面更整齊
    #     )
    
    # with col_btn_2:
    #     if st.button("🗑 刪除此原料", type="primary", use_container_width=True):
    #         st.session_state.selected_items = (
    #             st.session_state.selected_items
    #             .drop(st.session_state.selected_items.index[delete_index])
    #             .reset_index(drop=True)
    #         )
    #         st.rerun()

# # --------------------------
# # 顯示目前「已選原料清單」
# # --------------------------
# st.markdown("### 已選原料清單（可跨分類累積）")

# if st.session_state.selected_items.empty:
#     st.info("尚未加入任何原料。")
# else:
#     # ===========================
#     # 刪除原料
#     # ===========================
#     st.markdown("#### 刪除原料")
#     col_del_1, col_del_2 = st.columns([1, 4])
#     with col_del_1:
#         delete_index = st.number_input(
#             "行號",
#             min_value=0,
#             max_value=len(st.session_state.selected_items) - 1,
#             step=1,
#             value=0,
#             label_visibility="collapsed"
#         )
#     with col_del_2:
#         if st.button("🗑 刪除此原料"):
#             st.session_state.selected_items = (
#                 st.session_state.selected_items
#                 .drop(st.session_state.selected_items.index[delete_index])
#                 .reset_index(drop=True)
#             )
#             st.rerun() # 刪除後強制重整

#     st.markdown("---")

#     # ===========================
#     # 比例編輯
#     # ===========================
#     st.markdown("#### 請編輯各原料比例（%）")

#     edited_data = st.data_editor(
#         st.session_state.selected_items,
#         use_container_width=True,
#         hide_index=True,
#         key="selected_items_table",
#         disabled=["食品分類", "樣品名稱"] + [c for c in df.columns if c != "比例(%)"], # 鎖定除比例外的所有欄位
#         column_config={
#             "比例(%)": st.column_config.NumberColumn(
#                 "比例 (%)",
#                 min_value=0.0,
#                 max_value=100.0,
#                 step=0.1,
#                 format="%.1f",
#             )
#         },
#     )

#     # ===========================
#     # 即時計算加總
#     # ===========================
#     total_ratio = edited_data["比例(%)"].sum()
#     col1, col2 = st.columns([1, 2])
#     with col1:
#         st.metric("比例加總 (%)", f"{total_ratio:.1f}")
#     with col2:
#         if abs(total_ratio - 100.0) > 0.05:
#             st.warning("⚠️ 比例加總不等於 100%")
#         else:
#             st.success("✅ 比例加總為 100%")

#     # ===========================
#     # 手動套用
#     # ===========================
#     if st.button("✔ 套用比例修改"):
#         st.session_state.selected_items = edited_data.copy()
#         st.success("已套用最新比例")

st.markdown("---")
# --------------------------
# 步驟 3：顯示結果 (修正重點區)
# --------------------------
st.markdown("### 營養標示計算結果")

# 統一資料來源
calc_df = st.session_state.selected_items.copy()

# 1. 先計算原始資料的加權總和 (中文 Key)
final_nutrition_raw = {key: 0.0 for key in NUMERIC_FIELDS}

valid_data = calc_df[calc_df["比例(%)"] > 0]

if not valid_data.empty:
    for _, row in valid_data.iterrows():
        ratio = row["比例(%)"] / 100

        for col in NUMERIC_FIELDS:
            # 確保數值轉換安全
            val = pd.to_numeric(row[col], errors="coerce")
            if pd.isna(val):
                val = 0.0
            final_nutrition_raw[col] += val * ratio

# 2. 轉換為 HTML 標籤需要的格式 (英文 Key) 並計算熱量
# 這是你原本缺少的步驟，導致 HTML 抓不到資料
label_data = {
    "protein": final_nutrition_raw.get("粗蛋白(g)", 0),
    "fat": final_nutrition_raw.get("粗脂肪(g)", 0),
    "saturatedFat": final_nutrition_raw.get("飽和脂肪(g)", 0),
    "carbs": final_nutrition_raw.get("總碳水化合物(g)", 0),
    "sugar": final_nutrition_raw.get("糖質總量(g)", 0),
    "sodium": final_nutrition_raw.get("鈉(mg)", 0),
    "transFat": final_nutrition_raw.get("反式脂肪(mg)", 0), 
    "alcohol": final_nutrition_raw.get("酒精含量(g)", 0),
}

# 3. 計算熱量 (大卡) = 蛋白*4 + 脂肪*9 + 碳水*4
protein = round(label_data["protein"], 1)
fat     = round(label_data["fat"], 1)
carbs   = round(label_data["carbs"], 1)
alcohol = round(label_data["alcohol"], 1)

label_data["calories"] = round(
    protein * 4 +
    fat * 9 +
    carbs * 4 +
    alcohol * 7,
    1
)

# 使用者輸入的每一份標準
# input_serving_size = st.number_input("請輸入每份量（公克）", value=100.0, step=10.0)

# ==========================
# 輸入每份量與包裝份數
# ==========================
# 建立兩欄，讓輸入框並排比較好看，或者你要上下排也可以
col_input_a, col_input_b = st.columns(2)

with col_input_a:
    input_serving_size = st.number_input(
        "請輸入每份量（公克）", 
        min_value=1, 
        value=100,  # 設定為整數 int
        step=1      # 每次增減 1
    )

with col_input_b:
    # 新增：本包裝含幾份
    input_pack_servings = st.number_input(
        "本包裝含幾份", 
        min_value=1, 
        value=1,    # 設定為整數 int
        step=1      # 每次增減 1
    )


# 選擇是否顯示每日參考值(DV%)
show_dv = st.checkbox("顯示每日參考值百分比")
# 修改函式定義，增加 input_pack_servings 參數


def generate_nutrition_label_html(final_100g, input_serving_size, input_pack_servings, show_dv, daily_values):
    """
    生成三欄式營養標示 HTML
    """
    
    # ... (原本的 style 保持不變) ...
    style = """
    <style>
        /* ... 省略原本的 CSS ... */
        /* 請保留原本的 CSS 內容 */
        .nutrition-box {
            border: 2px solid #000;
            padding: 20px;
            width: 100%;
            max-width: 450px;
            background-color: #ffffff;
            color: #000000;
            font-family: "Microsoft JhengHei", sans-serif;
            line-height: 1.5;
            margin: 0 auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .nutrition-title {
            font-size: 22px;
            font-weight: 900;
            border-bottom: 3px solid #000;
            padding-bottom: 5px;
            margin-bottom: 10px;
            text-align: center;
        }
        .nutrition-meta {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 2px;
        }
        .nutrition-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #ccc;
            padding: 6px 0;
            font-size: 15px;
        }
        .nutrition-row:last-child {
            border-bottom: none;
        }
        .col-name {
            flex: 1;
            text-align: left;
            font-weight: bold;
        }
        .col-val {
            width: 100px;
            text-align: right;
            white-space: nowrap;
        }
        .indent {
            padding-left: 20px;
            font-weight: normal;
        }
        .header-row {
            font-weight: 900;
            border-bottom: 2px solid #000;
            align-items: flex-end;
        }
    </style>
    """

    nutrients_map = [
        ('calories', '熱量', '大卡', False),
        ('protein', '蛋白質', '公克', False),
        ('fat', '脂肪', '公克', False),
        ('saturatedFat', '飽和脂肪', '公克', True),
        ('transFat', '反式脂肪', '公克', True),
        ('carbs', '碳水化合物', '公克', False),
        ('sugar', '糖', '公克', True),
        ('sodium', '鈉', '毫克', False),
    ]

    col3_header = "每 100 公克" if not show_dv else "每日參考值百分比"
    
    # ==========================================
    # 修改這裡：使用傳入的 input_pack_servings
    # 並且 input_serving_size 改用整數顯示 (:.0f) 或保留小數皆可，這裡用整數
    # ==========================================
    rows_html = f"""
<div class="nutrition-meta">每一份量 {int(input_serving_size)} 公克</div>
<div class="nutrition-meta">本包裝含 {int(input_pack_servings)} 份</div>

<div class="nutrition-row header-row">
    <span class="col-name">項目</span>
    <span class="col-val">每份</span>
    <span class="col-val">{col3_header}</span>
</div>
"""
    
    for key, label, unit, is_indent in nutrients_map:
        val_100g = final_100g.get(key, 0.0)
        val_serving = val_100g * (input_serving_size / 100)
        str_serving = f"{val_serving:.1f} {unit}"

        if not show_dv:
            str_right = f"{val_100g:.1f} {unit}"
        else:
            dv_std = daily_values.get(key)
            if dv_std:
                dv_pct = (val_serving / dv_std) * 100
                str_right = f"{dv_pct:.1f} %"
            else:
                str_right = "*"

        indent_class = "indent" if is_indent else ""
        
        rows_html += f"""
<div class="nutrition-row">
    <span class="col-name {indent_class}">{label}</span>
    <span class="col-val">{str_serving}</span>
    <span class="col-val">{str_right}</span>
</div>
"""

    final_html = f"""
{style}
<div class="nutrition-box">
    <div class="nutrition-title">營養標示</div>
    {rows_html}
</div>
"""
    return final_html

# def generate_nutrition_label_html(final_100g, input_serving_size, show_dv, daily_values):
#     """
#     生成三欄式營養標示 HTML
#     final_100g: 必須包含英文 Key (calories, protein, fat...)
#     """
    
#     style = """
# <style>
#     .nutrition-box {
#         border: 2px solid #000;
#         padding: 20px;
#         width: 100%;
#         max-width: 450px;
#         background-color: #ffffff;
#         color: #000000;
#         font-family: "Microsoft JhengHei", sans-serif;
#         line-height: 1.5;
#         margin: 0 auto;
#         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
#     }
#     .nutrition-title {
#         font-size: 22px;
#         font-weight: 900;
#         border-bottom: 3px solid #000;
#         padding-bottom: 5px;
#         margin-bottom: 10px;
#         text-align: center;
#     }
#     .nutrition-meta {
#         font-size: 14px;
#         font-weight: bold;
#         margin-bottom: 2px;
#     }
#     .nutrition-row {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         border-bottom: 1px solid #ccc;
#         padding: 6px 0;
#         font-size: 15px;
#     }
#     .nutrition-row:last-child {
#         border-bottom: none;
#     }
#     .col-name {
#         flex: 1;
#         text-align: left;
#         font-weight: bold;
#     }
#     .col-val {
#         width: 100px;
#         text-align: right;
#         white-space: nowrap;
#     }
#     .indent {
#         padding-left: 20px;
#         font-weight: normal;
#     }
#     .header-row {
#         font-weight: 900;
#         border-bottom: 2px solid #000;
#         align-items: flex-end;
#     }
# </style>
# """

#     # 這裡的 Key 必須跟 label_data 和 DAILY_VALUES 的 Key 一致
#     nutrients_map = [
#         ('calories', '熱量', '大卡', False),
#         ('protein', '蛋白質', '公克', False),
#         ('fat', '脂肪', '公克', False),
#         ('saturatedFat', '飽和脂肪', '公克', True),
#         ('transFat', '反式脂肪', '公克', True),
#         ('carbs', '碳水化合物', '公克', False),
#         ('sugar', '糖', '公克', True),
#         ('sodium', '鈉', '毫克', False),
#         # ('alcohol', '酒精', '公克', False),   # 通常不列在營養標示中
#     ]

#     col3_header = "每 100 公克" if not show_dv else "每日參考值百分比"
    
#     rows_html = f"""
# <div class="nutrition-meta">每一份量 {input_serving_size:.1f} 公克</div>
# <div class="nutrition-meta">本包裝含 1 份</div>

# <div class="nutrition-row header-row">
#     <span class="col-name">項目</span>
#     <span class="col-val">每份</span>
#     <span class="col-val">{col3_header}</span>
# </div>
# """
    
#     for key, label, unit, is_indent in nutrients_map:
#         val_100g = final_100g.get(key, 0.0)
        
#         # 計算每份數值
#         val_serving = val_100g * (input_serving_size / 100)
#         str_serving = f"{val_serving:.1f} {unit}"

#         # 計算右側欄位
#         if not show_dv:
#             str_right = f"{val_100g:.1f} {unit}"
#         else:
#             dv_std = daily_values.get(key)
#             if dv_std:
#                 dv_pct = (val_serving / dv_std) * 100
#                 str_right = f"{dv_pct:.1f} %"
#             else:
#                 str_right = "*"

#         indent_class = "indent" if is_indent else ""
        
#         rows_html += f"""
# <div class="nutrition-row">
#     <span class="col-name {indent_class}">{label}</span>
#     <span class="col-val">{str_serving}</span>
#     <span class="col-val">{str_right}</span>
# </div>
# """

#     final_html = f"""
# {style}
# <div class="nutrition-box">
#     <div class="nutrition-title">營養標示</div>
#     {rows_html}
# </div>
# """
#     return final_html

# 顯示營養標示
st.markdown("### 最終營養標示")

# 這裡傳入修正後的 label_data
# 呼叫時加入 input_pack_servings
html_label = generate_nutrition_label_html(
    label_data, 
    input_serving_size, 
    input_pack_servings,  # 新增這個
    show_dv, 
    DAILY_VALUES
)
st.markdown(html_label, unsafe_allow_html=True)

# 提示每日參考值內容
if show_dv:
    st.caption("＊參考值未訂定")
    st.caption("每日參考值：熱量 2000 大卡、蛋白質 60 公克、脂肪 60 公克、飽和脂肪 18 公克、碳水化合物 300 公克、鈉 2000 毫克。")

# # 顯示計算數據（Debug 用：這裡顯示原始計算資料）
# with st.expander("🔍 查看詳細計算數據 (每 100g 原始值)"):
#     st.json(final_nutrition_raw)

# # 顯示轉換後的數據（Debug 用：確認 HTML 接收的資料是否正確）
# with st.expander("🔍 查看 HTML 渲染數據 (已轉換 Key)"):
#     st.json(label_data)