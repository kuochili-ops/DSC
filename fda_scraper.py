import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_fda_announcements():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for li in soup.select("li"):
        link = li.find("a")
        if not link:
            continue

        # 標題與連結
        title = link.get("title") or link.get_text(strip=True)
        href = "https://www.fda.gov" + link.get("href")

        # 🔎 抓 li 的文字前 10 個字元作為日期 (mm-dd-yyyy)
        text = li.get_text(strip=True)
        date_str = text[:10] if text[:10].count("-") == 2 else ""

        # ✅ 轉成 dd-mm-yyyy 格式
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
