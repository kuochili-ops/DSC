
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_fda_drug_safety_rss():
    """
    從 FDA RSS 取得藥品安全公告，回傳 DataFrame
    欄位：date, title, link
    """
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠ 無法取得 FDA RSS：{e}")
        return pd.DataFrame(columns=["date", "title", "link"])  # 回傳空表格

    # 解析 RSS XML
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    if not items:
        print("⚠ RSS 無資料，請檢查 FDA 網站或 RSS URL")
        return pd.DataFrame(columns=["date", "title", "link"])

    data = []
    for item in items:
        title = item.title.get_text(strip=True) if item.title else ""
        link = item.link.get_text(strip=True) if item.link else ""
        pub_date = item.pubDate.get_text(strip=True) if item.pubDate else ""
        data.append({"date": pub_date, "title": title, "link": link})

    return pd.DataFrame(data)
