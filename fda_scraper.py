
import requests
from bs4 import BeautifulSoup

def get_latest_communications():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return [{"date": "", "title": f"連線錯誤：{e}", "url": ""}]

    soup = BeautifulSoup(response.text, "html.parser")
    current_section = soup.find("h2", string="Current Drug Safety Communications")
    items = []

    if current_section:
        ul = current_section.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                text_parts = li.get_text(strip=True).split(" ", 1)
                date_text = text_parts[0] if len(text_parts) > 0 else ""
                link = li.find("a")
                if link:
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    full_url = href if href.startswith("http") else f"https://www.fda.gov{href}"
                    items.append({"date": date_text, "title": title, "url": full_url})

    if not items:
        items.append({"date": "", "title": "目前無新通報", "url": ""})

    return items
