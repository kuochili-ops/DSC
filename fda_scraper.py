import requests
from bs4 import BeautifulSoup
import pandas as pd

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

        # 直接抓 li 的前段文字 (包含 dd-mm-yyyy FDA ...)
        text = li.get_text(" ", strip=True)
        date_str = text.split(" ")[0:2]  # 前兩個字串 → 日期 + FDA
        date_fmt = " ".join(date_str)

        results.append({
            "date": date_fmt,   # 例如 "28-08-2025 FDA"
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
