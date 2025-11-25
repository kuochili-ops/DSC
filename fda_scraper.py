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

    # 找到 Current Drug Safety Communications 區塊
    current_section = soup.find("div", class_="view-current-drug-safety-communications")
    if not current_section:
        return pd.DataFrame()

    # 只抓取 Current 到 Previous 之間的公告
    for li in current_section.select("li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 日期在 <li> 前段，通常是 dd-mm-yyyy
        text = li.get_text(" ", strip=True)
        date_str = text.split(" ")[0] if "-" in text.split(" ")[0] else ""

        # 確保格式正確
        try:
            date_fmt = datetime.strptime(date_str, "%m-%d-%Y").strftime("%d-%m-%Y")
        except Exception:
            date_fmt = date_str  # 如果已經是 dd-mm-yyyy，就直接保留

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
