
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_fda_drug_safety_rss():
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
    }
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS: {e}")
        return pd.DataFrame()  # 回傳空表格

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    data = []
    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)
        pub_date = item.pubDate.get_text(strip=True)
        data.append({"date": pub_date, "title": title, "link": link})
    return pd.DataFrame(data)
