
import streamlit as st
import pandas as pd
from fda_scraper import fetch_fda_drug_safety_rss
from matcher import match_drugs
import io

st.title("FDA 藥品安全公告比對台灣藥品")

# Step 1: 抓取 FDA 公告
st.subheader("最新 FDA 藥品安全公告")
if st.button("更新公告"):
    with st.spinner("正在抓取 FDA 公告..."):
        fda_df = fetch_fda_drug_safety_rss()
        st.session_state['fda_df'] = fda_df
        st.success("公告更新完成！")

if 'fda_df' in st.session_state:
    st.dataframe(st.session_state['fda_df'])

# Step 2: 上傳台灣藥品資料
st.subheader("上傳台灣藥品 CSV")
uploaded_file = st.file_uploader("選擇 37_2c.csv", type="csv")

if uploaded_file and 'fda_df' in st.session_state:
    tw_df = pd.read_csv(uploaded_file)
    st.write(f"台灣藥品資料筆數：{len(tw_df)}")

    # Step 3: 比對
    if st.button("開始比對"):
        with st.spinner("比對中..."):
            result_df = match_drugs(st.session_state['fda_df'], uploaded_file)
            st.session_state['result_df'] = result_df
            st.success("比對完成！")

if 'result_df' in st.session_state:
    st.subheader("比對結果")
    st.dataframe(st.session_state['result_df'])

    # Step 4: 提供下載
    buffer = io.BytesIO()
    st.session_state['result_df'].to_excel(buffer, index=False)
    st.download_button(
        label="下載 Excel 報表",
        data=buffer,
        file_name="FDA_TW_Match.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
