
# fda_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_fda_announcements():
    """
    從 FDA Drug Safety Communications 頁面擷取公告資料
    回傳 DataFrame，欄位：date, title, url
    """
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("li")  # 抓取所有 <li>

    data = []
    for item in items:
        text = item.get_text(strip=True)
        link_tag = item.find("a")
        if link_tag:
            href = link_tag.get("href")
            title = link_tag.get_text(strip=True)
            date = text.split(" ")[0] if "-" in text.split(" ")[0] else ""
            full_url = "https://www.fda.gov" + href
            data.append({"date": date, "title": title, "url": full_url})

    return pd.DataFrame(data)

# 測試並輸出 CSV
if __name__ == "__main__":
    df = fetch_fda_announcements()
    df.to_csv("FDA_Announcements.csv", index=False)
    print("✅ 已輸出 FDA_Announcements.csv")
