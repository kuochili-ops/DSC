import streamlit as st
import pandas as pd
import io
from fda_scraper import fetch_fda_announcements
from matcher import match_drugs

st.set_page_config(page_title="FDA 藥品安全公告比對", layout="wide")
st.title("FDA 藥品安全公告比對台灣藥品")

def format_date(df, date_col="date"):
    if date_col in df.columns:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        df[date_col] = dates.dt.strftime("%d-%m-%Y")
        df[date_col] = df[date_col].where(dates.notna(), "")
    return df

# --- Step 1: 抓取 FDA 公告 ---
st.subheader("FDA 藥品安全公告")
st.markdown(
    "📌 來源：[Drug Safety Communications](https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications)"
)

if st.button("更新公告（FDA 網頁）"):
    with st.spinner("正在抓取 FDA 公告..."):
        fda_df = fetch_fda_announcements()
        if fda_df.empty:
            st.error("⚠ 無法取得 FDA 公告或沒有日期的項目。")
        else:
            fda_df = format_date(fda_df, date_col="date")
            st.session_state['fda_df'] = fda_df
            st.success(f"✅ 公告更新完成，共 {len(fda_df)} 筆資料。")

if 'fda_df' in st.session_state:
    st.subheader("FDA 藥品安全公告")
    st.dataframe(st.session_state['fda_df'][["date", "title", "text"]], use_container_width=True)
