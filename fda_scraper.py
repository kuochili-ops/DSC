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

    # 抓取所有 <ul><li>
    for li in soup.select("ul li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.fda.gov" + href

        text = link.get_text(strip=True)
        raw_date = li.get_text(" ", strip=True)[:10]  # 嘗試抓日期

        results.append({
            "date": raw_date,
            "title": title,
            "text": text,
            "url": href
        })

    df = pd.DataFrame(results)

    # 只保留有日期的項目
    if "date" in df.columns and not df.empty:
        df = df[df["date"].str.match(r"\d{2}-\d{2}-\d{4}", na=False)].copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d-%m-%Y")
        df["date"] = df["date"].fillna("")
        # 只保留最新 7 筆
        df = df.head(7)
    else:
        df = pd.DataFrame(columns=["date", "title", "text", "url"])

    return df
