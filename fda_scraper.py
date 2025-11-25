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

    for li in soup.select("ul li"):
        link = li.find("a")
        if not link:
            continue

        title = link.get("title") or link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = "https://www.fda.gov" + href

        raw_date = li.get_text(" ", strip=True)[:10]

        results.append({
            "date": raw_date,
            "title": f"[{title}]({href})",  # ✅ 標題直接附超連結
            "text": link.get_text(strip=True)  # 先顯示英文原文
        })

    df = pd.DataFrame(results)

    if "date" in df.columns and not df.empty:
        df = df[df["date"].str.match(r"\d{2}-\d{2}-\d{4}", na=False)].copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d-%m-%Y")
        df["date"] = df["date"].fillna("")
        df = df.head(7)
    else:
        df = pd.DataFrame(columns=["date", "title", "text"])

    return df
