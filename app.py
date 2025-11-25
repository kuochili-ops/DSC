import streamlit as st
import pandas as pd
import io
from datetime import datetime
from fda_scraper import fetch_fda_announcements
from matcher import match_drugs

st.set_page_config(page_title="FDA 藥品安全公告比對", layout="wide")
st.title("FDA 藥品安全公告比對台灣藥品")

def filter_dmy(df, date_col="date"):
    """保留開頭是日期的公告，不管後面有什麼字"""
    if date_col in df.columns:
        cleaned = df[date_col].astype(str).str.strip()
        def is_date_like(x):
            try:
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
            st.error("⚠ 無法取得 FDA 公告。")
        else:
            fda_df = filter_dmy(fda_df, date_col="date")
            st.session_state['fda_df'] = fda_df
            st.success(f"✅ 公告更新完成，共 {len(fda_df)} 筆資料。")

if 'fda_df' in st.session_state:
    st.write("📋 FDA 公告清單（只保留含日期的項目）：")
    st.dataframe(st.session_state['fda_df'], use_container_width=True)

# --- Step 2: 直接讀取台灣藥品資料（同目錄固定檔案） ---
st.subheader("台灣藥品資料（自動載入）")
try:
    tw_df = pd.read_csv("37_2c.csv")   # ✅ 同目錄直接讀取
    st.write(f"📦 台灣藥品資料筆數：{len(tw_df)}")
    st.session_state['tw_df'] = tw_df
except Exception as e:
    st.error(f"⚠ 無法讀取台灣藥品資料：{e}")

# --- Step 3: 比對 ---
if 'fda_df' in st.session_state and 'tw_df' in st.session_state:
    if st.button("開始比對"):
        with st.spinner("比對中..."):
            result_df, special_df = match_drugs(st.session_state['fda_df'], st.session_state['tw_df'])
            st.session_state['result_df'] = result_df
            st.session_state['special_df'] = special_df
            st.success(f"✅ 比對完成，共 {len(result_df)} 筆公告。")

# --- Step 4: 顯示結果 ---
if 'result_df' in st.session_state:
    st.subheader("比對結果（完整）")
    st.dataframe(st.session_state['result_df'], use_container_width=True)

if 'special_df' in st.session_state:
    st.subheader("匹配到『中國化學』或『中化裕民』的公告")
    st.dataframe(st.session_state['special_df'], use_container_width=True)

    buffer = io.BytesIO()
    st.session_state['special_df'].to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 下載專屬報表",
        data=buffer,
        file_name="FDA_TW_Special.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
