import streamlit as st
from fda_scraper import get_latest_communications
from taiwan_drug_match import match_taiwan_drugs
from report_generator import create_html_report
from utils.config_loader import load_config

# Streamlit 標題
st.title("FDA 藥品安全監控報告")

# 讀取設定檔
config = load_config("config.yaml")

# Step 1: 擷取 FDA 最新通報（RSS）
st.subheader("正在擷取 FDA 最新藥品安全通訊...")
fda_data = get_latest_communications()

if not fda_data or (len(fda_data) == 1 and fda_data[0]["title"] == "目前無新通報"):
    st.warning("目前無新通報")
else:
    st.success(f"共取得 {len(fda_data)} 筆資料")

    # 顯示 FDA 通報列表（前 10 筆）
    st.write("### FDA 最新通報列表")
    for item in fda_data[:10]:
        st.markdown(f"- **{item['date']}** | [{item['title']}]({item['url']})")

    # Step 2: 比對台灣藥品資料
    st.subheader("比對台灣藥品許可證資料...")
    taiwan_data = match_taiwan_drugs(fda_data, csv_path="37_2c.csv")

    # Step 3: 產生 HTML 報告
    report_html = create_html_report(taiwan_data)

    # Step 4: 顯示報告
    st.subheader("報告結果")
    st.markdown(report_html, unsafe_allow_html=True)
