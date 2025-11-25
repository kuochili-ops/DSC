import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_fda_announcements():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        return pd.DataFrame()

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # 公告在 div.views-row 裡
    for row in soup.select("div.views-row"):
        title_tag = row.select_one("div.views-field-title a")
        date_tag = row.select_one("span.date-display-single")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href")
        if href and not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 日期處理
        if date_tag:
            raw_date = date_tag.get_text(strip=True)
            try:
                date_fmt = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%d-%m-%Y")
            except Exception:
                date_fmt = raw_date
        else:
            date_fmt = ""

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
