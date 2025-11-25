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
    # FDA 公告通常在 <li> 或 <div class="views-row"> 裡
    for li in soup.select("li, div.views-row"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if not href:
            continue  # 跳過沒有 href 的項目
        if not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 嘗試抓日期：在 <li> 的文字前段
        text = li.get_text(" ", strip=True)
        date_str = text[:10] if text[:10].count("-") == 2 else ""

        try:
            date_fmt = datetime.strptime(date_str, "%m-%d-%Y").strftime("%d-%m-%Y")
        except Exception:
            date_fmt = ""

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
