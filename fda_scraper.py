
import requests
from bs4 import BeautifulSoup

def get_latest_communications():
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 擷取 FDA 通報列表
    items = []
    for link in soup.select(".view-content .views-row"):
        drug_name = link.get_text(strip=True)
        href = link.find("a")["href"]
        items.append({
            "drug_name": drug_name,
            "url": f"https://www.fda.gov{href}"
        })
    return items
