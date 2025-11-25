import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_fda_announcements():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception:
        return pd.DataFrame()

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # 公告清單在 .article-text 裡的 <li>
    for li in soup.select("div.article-text ul li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 日期在 <li> 前段，取前 10 個字元
        text = li.get_text(" ", strip=True)
        date_str = text[:10]

        try:
            # 如果是 mm-dd-yyyy → 轉成 dd-mm-yyyy
            date_fmt = datetime.strptime(date_str, "%m-%d-%Y").strftime("%d-%m-%Y")
        except Exception:
            # 如果已經是 dd-mm-yyyy → 保留
            date_fmt = date_str

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
