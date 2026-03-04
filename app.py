import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import numpy as np

# ==========================
# Page config
# ==========================
st.set_page_config(
    page_title="NutriTag｜台灣營養標示計算工具",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# Load data
# ==========================
DATA_FILE = "selected_columns.csv"

if not os.path.exists(DATA_FILE):
    st.error(f"找不到檔案 `{DATA_FILE}`，請確認是否放在同一目錄內。")
    st.stop()

df = pd.read_csv(DATA_FILE)
df.dropna(subset=["食品分類", "樣品名稱"], inplace=True)
df.fillna(0, inplace=True)

FOOD_CATEGORIES = (
    df["食品分類"]
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

NUMERIC_FIELDS = [
    "粗蛋白(g)", "粗脂肪(g)", "飽和脂肪(g)",
    "總碳水化合物(g)", "糖質總量(g)",
    "鈉(mg)", "反式脂肪(mg)", "酒精含量(g)"
]

DAILY_VALUES = {
    "calories": 2000.0,
    "protein": 60.0,
    "fat": 60.0,
    "saturatedFat": 18.0,
    "carbs": 300.0,
    "sodium": 2000.0,
    "transFat": None,
    "sugar": None,
}

# ==========================
# Header
# ==========================
st.title("NutriTag｜台灣營養標示計算工具")
st.caption("依據台灣食品標示法規，快速產生營養標示")

# ==========================
# Session state
# ==========================
if "selected_items" not in st.session_state:
    st.session_state.selected_items = df.iloc[0:0].copy()
    st.session_state.selected_items["比例(%)"] = pd.Series(dtype="float64")

# ==========================
# Sidebar - 即時搜尋（分類 / 關鍵字）
# ==========================
st.sidebar.header("加入原料")

search_keyword = st.sidebar.text_input(
    "🔍 搜尋原料名稱",
    placeholder="輸入關鍵字（例：糖、油、奶）",
    key="ingredient_search"
)

food_category = st.sidebar.selectbox(
    "選擇食品分類",
    ["全部分類"] + FOOD_CATEGORIES,
    key="ingredient_category"
)

# --- 篩選資料 ---
browse_df = df.copy()

if food_category != "全部分類":
    browse_df = browse_df[browse_df["食品分類"] == food_category]

if search_keyword:
    browse_df = browse_df[
        browse_df["樣品名稱"]
        .astype(str)
        .str.contains(search_keyword, case=False, na=False)
    ]

# --- 篩選資料 ---
browse_df = df.copy()

if food_category != "全部分類":
    browse_df = browse_df[browse_df["食品分類"] == food_category]

if search_keyword:
    browse_df = browse_df[
        browse_df["樣品名稱"]
        .astype(str)
        .str.contains(search_keyword, case=False, na=False)
    ]

# ==========================
# Sidebar - 分頁瀏覽 + 搜尋共存
# ==========================

PAGE_SIZE = 20

# --- 分頁狀態 ---
if "browse_page" not in st.session_state:
    st.session_state.browse_page = 0

# 🔑 搜尋或分類改變時，自動回到第 1 頁
if "prev_search" not in st.session_state:
    st.session_state.prev_search = (search_keyword, food_category)

if st.session_state.prev_search != (search_keyword, food_category):
    st.session_state.browse_page = 0
    st.session_state.prev_search = (search_keyword, food_category)

total = len(browse_df)

# --- 若完全沒條件，不顯示 ---
if not search_keyword and food_category == "全部分類":
    st.sidebar.info("請輸入關鍵字或選擇食品分類")
elif total == 0:
    st.sidebar.info("找不到符合條件的原料")
else:
    start = st.session_state.browse_page * PAGE_SIZE
    end = start + PAGE_SIZE

    # --- 分頁控制 ---
    col_prev, col_info, col_next = st.sidebar.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️", use_container_width=True):
            st.session_state.browse_page = max(0, st.session_state.browse_page - 1)

    with col_info:
        st.caption(
            f"顯示第 {start + 1}–{min(end, total)} / {total} 筆"
        )

    with col_next:
        if st.button("➡️", use_container_width=True):
            if end < total:
                st.session_state.browse_page += 1

    st.sidebar.markdown("---")

    # --- 顯示目前頁 ---
    for _, row in browse_df.iloc[start:end].iterrows():
        name = row["樣品名稱"]

        if st.sidebar.button(
            f"➕ {name}",
            key=f"add_{name}_{start}",
            use_container_width=True
        ):
            existing_names = (
                st.session_state.selected_items["樣品名稱"]
                .astype(str)
                .values
            )

            if name in existing_names:
                st.sidebar.warning("⚠️ 此原料已加入")
            else:
                new_row = row.copy()
                new_row["比例(%)"] = 0.0

                st.session_state.selected_items = pd.concat(
                    [
                        st.session_state.selected_items,
                        pd.DataFrame([new_row])
                    ],
                    ignore_index=True
                )

                st.sidebar.success(f"✅ 已加入：{name}")
                st.rerun()

# ==========================

# Sidebar：資料來源與使用說明

# ==========================

with st.sidebar.expander("📘 資料來源與使用說明"):

    st.markdown("""

    本工具所使用之原料營養成分資料，主要引用自：  

    衛生福利部食品藥物管理署（TFDA）  

    食品營養成分資料庫（新版）  

    https://consumer.fda.gov.tw/Food/TFND.aspx?nodeID=178  

    使用說明與免責聲明  

    本工具係依使用者輸入之配方比例，  

    進行營養成分試算與加總，僅作為  

    食品研發、配方試算及營養標示規劃之輔助工具。  

    實際產品之營養標示數值，  

    仍應依產品實際檢驗結果，  

    並依「包裝食品營養標示應遵行事項」  

    及相關法規規定進行最終確認。

    """)

# # ==========================
# # Sidebar - 搜尋 + 加入原料（✅穩定版）
# # ==========================
# st.sidebar.header("加入原料")

# # --- 搜尋條件（固定 key）---
# search_keyword = st.sidebar.text_input(
#     "🔍 搜尋原料名稱<br>（輸入後點“選擇樣品名稱”）",
#     placeholder="輸入關鍵字（例：糖、油、奶）",
#     key="ingredient_search"
# )

# food_category = st.sidebar.selectbox(
#     "選擇食品分類",
#     ["全部分類"] + FOOD_CATEGORIES,
#     key="ingredient_category"
# )

# # --- 篩選資料 ---
# browse_df = df.copy()

# if food_category != "全部分類":
#     browse_df = browse_df[browse_df["食品分類"] == food_category]

# if search_keyword:
#     browse_df = browse_df[
#         browse_df["樣品名稱"]
#         .astype(str)
#         .str.contains(search_keyword, case=False, na=False)
#     ]

# # --- 準備選項 ---
# options = ["請選擇"] + browse_df["樣品名稱"].tolist()

# # 🔑 關鍵：搜尋條件變動時，重設 selectbox
# if "ingredient_selectbox" in st.session_state:
#     if st.session_state.ingredient_selectbox not in options:
#         st.session_state.ingredient_selectbox = "請選擇"

# # --- 顯示選單 ---
# if browse_df.empty:
#     st.sidebar.info("找不到符合條件的原料")
# else:
#     sample_name = st.sidebar.selectbox(
#         "選擇樣品名稱",
#         options=options,
#         key="ingredient_selectbox"
#     )

#     # --- 加入原料 ---
#     if sample_name != "請選擇":
#         selected_row = (
#             browse_df[browse_df["樣品名稱"] == sample_name]
#             .iloc[0]
#             .copy()
#         )

#         if st.sidebar.button("➕ 加入原料", use_container_width=True):

#             existing_names = (
#                 st.session_state.selected_items["樣品名稱"]
#                 .astype(str)
#                 .values
#             )

#             if sample_name in existing_names:
#                 st.sidebar.warning("⚠️ 此原料已加入")
#             else:
#                 selected_row["比例(%)"] = 0.0
#                 st.session_state.selected_items = pd.concat(
#                     [
#                         st.session_state.selected_items,
#                         pd.DataFrame([selected_row])
#                     ],
#                     ignore_index=True
#                 )
#                 st.sidebar.success(f"✅ 已加入：{sample_name}")

# ==========================
# Selected ingredients table
# ==========================
st.markdown("### 已選原料清單")

if st.session_state.selected_items.empty:
    st.info("尚未加入任何原料。")
else:
    edited = st.data_editor(
        st.session_state.selected_items,
        use_container_width=True,
        hide_index=True,
        column_config={
            "比例(%)": st.column_config.NumberColumn(
                "比例 (%)", min_value=0.0, max_value=100.0, step=0.1
            )
        }
    )

    total_ratio = edited["比例(%)"].sum()
    if abs(total_ratio - 100) > 0.05:
        st.warning("⚠️ 比例加總不等於 100%")
    else:
        st.success("✅ 比例加總為 100%")

    if st.button("✔ 套用比例修改"):
        st.session_state.selected_items = edited.copy()
        st.success("已套用")

# ==========================
# 刪除原料功能
# ==========================
st.markdown("---")
st.markdown("#### （選填）刪除原料")

col_del_1, col_del_2 = st.columns([4, 1.5])

with col_del_1:
    delete_options = [
        f"{i+1}. {row['樣品名稱']}"
        for i, row in st.session_state.selected_items.iterrows()
    ]

    delete_target = st.selectbox(
        "選擇要刪除的原料",
        options=delete_options,
        label_visibility="collapsed"
    )

with col_del_2:
    if st.button("🗑 刪除此原料", type="primary", use_container_width=True):
        idx_to_drop = delete_options.index(delete_target)

        st.session_state.selected_items = (
            st.session_state.selected_items
            .drop(st.session_state.selected_items.index[idx_to_drop])
            .reset_index(drop=True)
        )

        st.rerun()

# ==========================
# Calculate nutrition (per 100g)
# ==========================
calc_df = st.session_state.selected_items.copy()
final_raw = {k: 0.0 for k in NUMERIC_FIELDS}

for _, row in calc_df[calc_df["比例(%)"] > 0].iterrows():
    r = row["比例(%)"] / 100
    for col in NUMERIC_FIELDS:
        final_raw[col] += pd.to_numeric(row[col], errors="coerce") * r

label_data = {
    "protein": final_raw["粗蛋白(g)"],
    "fat": final_raw["粗脂肪(g)"],
    "saturatedFat": final_raw["飽和脂肪(g)"],
    "carbs": final_raw["總碳水化合物(g)"],
    "sugar": final_raw["糖質總量(g)"],
    "sodium": final_raw["鈉(mg)"],
    "transFat": final_raw["反式脂肪(mg)"],
}

label_data["calories"] = round(
    label_data["protein"] * 4 +
    label_data["fat"] * 9 +
    label_data["carbs"] * 4,
    1
)

# ==========================
# Serving size input
# ==========================
st.markdown("### 營養標示計算結果")

c1, c2 = st.columns(2)
with c1:
    serving_size = st.number_input("每一份量（公克）", min_value=1, value=100)
with c2:
    pack_servings = st.number_input("本包裝含幾份", min_value=1, value=1)

show_dv = st.checkbox("顯示每日參考值百分比")


def fmt_val(value, decimals=1):
    """
    若數值為 0 或 0.0 → 顯示 '0'
    其餘 → 依 decimals 顯示小數
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if abs(value) < 1e-9:
        return "0"
    return f"{value:.{decimals}f}"

# ==========================
# HTML fragment (for preview)
# ==========================
def generate_html_fragment(
    data,
    serving_size,
    pack_servings,
    show_dv,
    daily_values,
    label_size
):
    size_css = get_label_css(label_size)

    style = f"""
    <style>
        .nutrition-box {{
            --box-padding: 12px;

            border: 2px solid #000;
            padding: var(--box-padding);
            font-family: "Microsoft JhengHei", sans-serif;
            background: #fff;
            box-sizing: border-box;
        }}

        /* ===== 共用：讓結構線左右貼齊外框 ===== */
        .nutrition-title,
        .nutrition-meta-row,
        .nutrition-header {{
            margin-left: calc(-1 * var(--box-padding));
            margin-right: calc(-1 * var(--box-padding));
            padding-left: var(--box-padding);
            padding-right: var(--box-padding);
        }}

        /* ===== 標題 ===== */
        .nutrition-title {{
            font-size: 20px;
            font-weight: normal;
            text-align: center;
            padding-bottom: 4px;
            margin-bottom: 6px;
            border-bottom: 1.5px solid #000;   /* 黑線① */
        }}

        /* ===== 每一份量 / 本包裝含 ===== */
        .nutrition-meta-row {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: normal;
            padding-bottom: 4px;
            margin-bottom: 6px;
            border-bottom: 1.5px solid #000;   /* 黑線② */
        }}

        /* ===== 表頭 ===== */
        .nutrition-header {{
            display: grid;
            grid-template-columns: 1fr 90px 120px;
            font-size: 13px;
            font-weight: normal;
            padding-bottom: 4px;
            margin-bottom: 4px;
            border-bottom: 1.5px solid #000;   /* 黑線③ */
        }}

        /* ===== 一般營養素列（完全無線） ===== */
        .nutrition-row {{
            display: grid;
            grid-template-columns: 1fr 90px 120px;
            font-size: 13px;
            padding: 3px 0;
            font-weight: normal;
        }}

        .col-right {{
            text-align: right;
            white-space: nowrap;
            padding-left: 4px;   /* 數值一點點間距 */
        }}

        .indent {{
            # padding-left: 16px;
            text-indent: 1em;
            font-weight: normal;
        }}

        .nutrition-dv-note {{
            font-size: 11px;
            line-height: 1.4;
            margin-top: 6px;
            color: #000;
        }}

        {size_css}
    </style>
    """

    nutrients = [
        ("calories", "熱量", "大卡", False),
        ("protein", "蛋白質", "公克", False),
        ("fat", "脂肪", "公克", False),
        ("saturatedFat", "飽和脂肪", "公克", True),
        ("transFat", "反式脂肪", "公克", True),
        ("carbs", "碳水化合物", "公克", False),
        ("sugar", "糖", "公克", True),
        ("sodium", "鈉", "毫克", False),
    ]

    col3_header = "每日參考值百分比" if show_dv else "每 100 公克"

    rows_html = f"""
    <div class="nutrition-meta-row">
        <span>每一份量 {int(serving_size)} 公克</span>
        <span>本包裝含 {int(pack_servings)} 份</span>
    </div>

    <div class="nutrition-header">
        <div>項目</div>
        <div class="col-right">每份</div>
        <div class="col-right">{col3_header}</div>
    </div>
    """

    for key, label, unit, indent in nutrients:
        per_100g = data.get(key, 0.0)
        per_serving = per_100g * serving_size / 100

        if show_dv:
            dv = daily_values.get(key)
            if dv:
                dv_pct = per_serving / dv * 100
                # right_col = f"{dv_pct:.1f} %"
                right_col = f"{fmt_val(dv_pct)} %"
            else:
                right_col = "*"
        else:
            # right_col = f"{per_100g:.1f} {unit}"
            right_col = f"{per_100g:.1f} {unit}"

        rows_html += f"""
        <div class="nutrition-row">
            <div class="{ 'indent' if indent else '' }">{label}</div>
            
            <div class="col-right">{fmt_val(per_serving)} {unit}</div>
            <div class="col-right">{right_col}</div>
        </div>

        """
        dv_note_html = ""
        if show_dv:
            dv_note_html = """
            <div class="nutrition-dv-note">
                <br>
                每日參考值：熱量 2000 大卡、蛋白質 60 公克、脂肪 60 公克、飽和脂肪 18 公克、
                碳水化合物 300 公克、鈉 2000 毫克。
            </div>
            """

    return f"""
    {style}
    <div class="nutrition-box">
        <div class="nutrition-title">營養標示</div>
        {rows_html}
        {dv_note_html}
    </div>
    """
# ==========================
# Wrap full HTML (for download)
# ==========================
def wrap_full_html(fragment):
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>營養標示</title>
</head>
<body>
{fragment}
</body>
</html>
"""

st.markdown("### 標籤輸出設定")

label_size = st.radio(
    "選擇標籤尺寸（測試版）",
    [
        "標籤 9 × 8.5 cm（建議）",
        "標籤 9 × 8 cm",
        "標籤 9 × 7.5 cm"
    ],
    horizontal=True
)

def get_label_css(label_size):
    if label_size == "標籤 9 × 8.5 cm（建議）":
        return """
        .nutrition-box {
            width: 9cm;
            height: 8.5cm;
        }
        .nutrition-title {
            font-size: 20px;
            margin-bottom: 4px;
        }
        .nutrition-row {
            font-size: 13.5px;
            padding: 3px 0;
        }
        .nutrition-meta-row {
            font-size: 13px;
            margin-bottom: 4px;
        }
        @page {
            size: 9cm 8.5cm;
            margin: 0.45cm;
        }
        """

    elif label_size == "標籤 9 × 8 cm":
        return """
        .nutrition-box {
            width: 9cm;
            height: 8cm;
        }
        .nutrition-title {
            font-size: 19.5px;
            margin-bottom: 4px;
        }
        .nutrition-row {
            font-size: 13px;
            padding: 2.5px 0;
        }
        .nutrition-meta-row {
            font-size: 12.8px;
            margin-bottom: 3px;
        }
        @page {
            size: 9cm 8cm;
            margin: 0.4cm;
        }
        """

    else:  # 標籤 9 × 7.5 cm（極限）
        return """
        .nutrition-box {
            width: 9cm;
            height: 7.5cm;
        }
        .nutrition-title {
            font-size: 19px;
            margin-bottom: 3px;
        }
        .nutrition-row {
            font-size: 12.5px;
            padding: 2px 0;
        }
        .nutrition-meta-row {
            font-size: 12.5px;
            margin-bottom: 2px;
        }
        @page {
            size: 9cm 7.5cm;
            margin: 0.35cm;
        }
        """
# ==========================
# Render
# ==========================
html_fragment = generate_html_fragment(
    label_data,
    serving_size,
    pack_servings,
    show_dv,
    DAILY_VALUES,
    label_size
)

components.html(
    html_fragment,
    height=700 if label_size == "A4 列印版" else 420,
    scrolling=True
)

# 提示每日參考值內容（畫面顯示用）
# if show_dv:
#     st.caption("＊參考值未訂定")
#     st.caption(
#         "每日參考值：熱量 2000 大卡、蛋白質 60 公克、"
#         "脂肪 60 公克、飽和脂肪 18 公克、"
#         "碳水化合物 300 公克、鈉 2000 毫克。"
#     )

html_download = wrap_full_html(html_fragment)

st.download_button(
    "⬇️ 下載營養標示（HTML｜已套用尺寸）",
    data=html_download.encode("utf-8"),
    file_name="nutrition_label.html",
    mime="text/html; charset=utf-8",
    use_container_width=True
)

st.caption("下載後可直接列印或另存為 PDF，版面已依所選尺寸設定。")

