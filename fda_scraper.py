import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_fda_announcements():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching FDA announcements: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    for li in soup.select("div.article-text ul li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.fda.gov" + href

        text = link.get_text(strip=True)
        raw_date = li.get_text(" ", strip=True)[:10]  # 只取日期部分

        results.append({
            "date": raw_date,
            "title": title,
            "text": text,
            "url": href
        })

    df = pd.DataFrame(results)

    # 防呆：確保有 date 欄位才轉換
    if "date" in df.columns and not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d-%m-%Y")
        df["date"] = df["date"].fillna("")
    else:
        df["date"] = ""

    return df
