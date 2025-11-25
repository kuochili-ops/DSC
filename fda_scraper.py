import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_fda_announcements():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
    except Exception:
        return pd.DataFrame()

    if res.status_code != 200:
        return pd.DataFrame()

    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    # FDA 公告通常在 div.views-row 裡
    for row in soup.select("div.views-row"):
        link = row.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 日期通常在 span.date-display-single
        date_tag = row.find("span", class_="date-display-single")
        if date_tag:
            raw_date = date_tag.get_text(strip=True)
            try:
                # FDA 頁面日期格式通常是 mm/dd/yyyy
                date_fmt = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%d-%m-%Y")
            except Exception:
                date_fmt = ""
        else:
            date_fmt = ""

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
