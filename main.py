
from fda_scraper import get_latest_communications
from taiwan_drug_match import match_taiwan_drugs
from report_generator import create_html_report
from utils.config_loader import load_config

def main():
    config = load_config("config.yaml")
    fda_data = get_latest_communications()
    taiwan_data = match_taiwan_drugs(fda_data, csv_path="37_2c.csv")
    report_html = create_html_report(taiwan_data)

    # 測試輸出 HTML 報告
    print(report_html)

if __name__ == "__main__":
    main()
