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

    # 找到 Current Drug Safety Communications 區塊
    current_section = soup.find("div", class_="view-current-drug-safety-communications")
    if not current_section:
        return pd.DataFrame()

    # 在該區塊內抓所有 <li>
    for li in current_section.select("ul > li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://www.fda.gov" + href

        # 日期在 <li> 前段，取前 10 個字元
        text = li.get_text(" ", strip=True)
        date_str = text[:10]

        try:
            date_fmt = datetime.strptime(date_str, "%m-%d-%Y").strftime("%d-%m-%Y")
        except Exception:
            date_fmt = date_str  # 如果已經是 dd-mm-yyyy 就保留

        results.append({
            "date": date_fmt,
            "title": title,
            "url": href
        })

    return pd.DataFrame(results)
