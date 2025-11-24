
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_fda_drug_safety():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 抓取公告列表
    items = soup.select("div.views-row")
    data = []
    for item in items:
        date_tag = item.select_one(".date-display-single")
        title_tag = item.select_one("h3 a")
        if date_tag and title_tag:
            date = date_tag.get_text(strip=True)
            title = title_tag.get_text(strip=True)
            link = "https://www.fda.gov" + title_tag.get("href")
            data.append({"date": date, "title": title, "link": link})
    
    return pd.DataFrame(data)
