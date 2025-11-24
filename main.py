
# main.py
from fda_scraper import get_latest_communications
from taiwan_drug_match import match_taiwan_drugs
from report_generator import create_html_report
from email_sender import send_email
from utils.config_loader import load_config

def main():
    # Step 1: 讀取設定檔
    config = load_config("config.yaml")

    # Step 2: 抓取 FDA 最新通報
    fda_data = get_latest_communications()

    # Step 3: 比對台灣藥品（使用 37_2c.csv）
    taiwan_data = match_taiwan_drugs(fda_data, csv_path="37_2c.csv")

    # Step 4: 產生報告
    report_html = create_html_report(fda_data, taiwan_data)

    # Step 5: 發送 Email
    send_email(report_html, config["recipients"])

if __name__ == "__main__":
    main()
