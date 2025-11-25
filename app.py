import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from fda_scraper import fetch_fda_announcements
from matcher import match_drugs

st.set_page_config(page_title="FDA 藥品安全公告比對", layout="wide")
st.title("FDA 藥品安全公告比對台灣藥品")

def filter_dmy(df, date_col="date"):
    """保留開頭是日期的公告，不管後面有什麼字"""
    if date_col in df.columns:
        # 先去除前後空白與不可見字元
        cleaned = df[date_col].astype(str).str.strip()

        def is_date_like(x):
            try:
                # 嘗試解析前 10 個字元
                datetime.strptime(x[:10], "%m-%d-%Y")
                return True
            except ValueError:
                return False

        mask = cleaned.apply(is_date_like)
        df = df.copy()
        df[date_col] = cleaned
        return df[mask].copy()
    return df

# --- Step 1: 抓取 FDA 公告 ---
st.subheader("最新 FDA 藥品安全公告")
if st.button("更新公告（FDA 網頁）"):
    with st.spinner("正在抓取 FDA 公告..."):
        fda_df = fetch_fda_announcements()
        if fda_df.empty:
            st.error("⚠ 無法取得 FDA 公告，請改用 CSV 上傳模式。")
        else:
            # ✅ 過濾掉非日期的項目
            fda_df = filter_dmy(fda_df, date_col="date")
            st.session_state['fda_df'] = fda_df
            st.success(f"✅ 公告更新完成，共 {len(fda_df)} 筆資料。")

# 顯示擷取結果
if 'fda_df' in st.session_state:
    st.write("📋 FDA 公告清單（只保留含日期的項目）：")
    st.dataframe(st.session_state['fda_df'], use_container_width=True)

# --- Step 2: 上傳 FDA 公告 CSV（備援模式） ---
st.subheader("或上傳 FDA 公告 CSV（備援）")
fda_csv = st.file_uploader("選擇 FDA 公告 CSV", type="csv")
if fda_csv:
    fda_df = pd.read_csv(fda_csv)
    fda_df = filter_dmy(fda_df, date_col="date")  # ✅ 過濾
    st.session_state['fda_df'] = fda_df
    st.success(f"✅ 已載入 FDA 公告 CSV，共 {len(fda_df)} 筆資料。")

# --- Step 3: 上傳台灣藥品資料 ---
st.subheader("上傳台灣藥品 CSV（必須）")
uploaded_file = st.file_uploader("選擇 37_2c.csv", type="csv")

if uploaded_file and 'fda_df' in st.session_state:
    tw_df = pd.read_csv(uploaded_file)
    st.write(f"📦 台灣藥品資料筆數：{len(tw_df)}")

    # --- Step 4: 比對 ---
    if st.button("開始比對"):
        with st.spinner("比對中..."):
            result_df = match_drugs(st.session_state['fda_df'], tw_df)
            st.session_state['result_df'] = result_df
            st.success(f"✅ 比對完成，共 {len(result_df)} 筆公告。")

# --- Step 5: 顯示結果與下載 ---
if 'result_df' in st.session_state:
    st.subheader("比對結果")
    st.dataframe(st.session_state['result_df'], use_container_width=True)

    buffer = io.BytesIO()
    st.session_state['result_df'].to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 下載 Excel 報表",
        data=buffer,
        file_name="FDA_TW_Match.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
