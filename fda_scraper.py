
import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_fda_drug_safety_rss():
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(rss_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    data = []
    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)
        pub_date = item.pubDate.get_text(strip=True)
        data.append({"date": pub_date, "title": title, "link": link})
    return pd.DataFrame(data)

import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_fda_drug_safety_rss():
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(rss_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    data = []
    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)
        pub_date = item.pubDate.get_text(strip=True)
        data.append({"date": pub_date, "title": title, "link": link})
    return pd.DataFrame(data)
