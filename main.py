
import streamlit as st
from fda_scraper import get_fda_current_communications
from taiwan_drug_match import match_taiwan_drugs
from report_generator import create_html_report, export_to_csv

st.title("FDA 藥品安全監控報告")

# Step 1: 擷取 FDA 最新通報
st.subheader("擷取 FDA 最新藥品安全通訊...")
fda_data = get_fda_current_communications()

if not fda_data or (len(fda_data) == 1 and fda_data[0]["title"] == "目前無新通報"):
    st.warning("目前無新通報")
else:
    st.success(f"共取得 {len(fda_data)} 筆資料")
    st.write("### FDA 最新通報列表")
    for item in fda_data[:10]:
        st.markdown(f"- **{item['date']}** | [{item['title']}]({item['url']})")

    # Step 2: 比對台灣藥品資料
    st.subheader("比對台灣藥品許可證資料...")
    taiwan_data = match_taiwan_drugs(fda_data, csv_path="37_2c.csv")

    # Step 3: 顯示報告
    report_html = create_html_report(taiwan_data)
    st.subheader("報告結果")
    st.markdown(report_html, unsafe_allow_html=True)

    # Step 4: 提供 CSV 下載
    export_to_csv(taiwan_data)

    with open("FDA_Taiwan_Match.csv", "rb") as f:
        st.download_button("下載比對結果 CSV", data=f, file_name="FDA_Taiwan_Match.csv")
