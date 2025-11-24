
import requests
from bs4 import BeautifulSoup

def get_latest_communications():
    """
    抓取 FDA 官方頁面最新的 Current Drug Safety Communications 列表
    回傳格式：
    [
        {
            "date": "08-28-2025",
            "title": "FDA to recommend additional, earlier MRI monitoring for patients with Alzheimer’s disease taking Leqembi (lecanemab)",
            "url": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-recommend-additional-earlier-mri-monitoring-patients-alzheimers-disease-taking-leqembi-lecanemab"
        },
        ...
    ]
    """
    url = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return [{"date": "", "title": f"連線錯誤：{e}", "url": ""}]

    soup = BeautifulSoup(response.text, "html.parser")

    # 找到 Current Drug Safety Communications 區塊
    current_section = soup.find("h2", string="Current Drug Safety Communications")
    items = []

    if current_section:
        ul = current_section.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                # 擷取日期與標題
                text_parts = li.get_text(strip=True).split(" ", 1)
                date_text = text_parts[0] if len(text_parts) > 0 else ""
                link = li.find("a")
                if link:
                    title = link.get_text(strip=True)
                    href = link["href"]

                    # 修正 URL 拼接邏輯
                    if href.startswith("http"):
                        full_url = href
                    else:
                        full_url = f"https://www.fda.gov{href}"

                    items.append({
                        "date": date_text,
                        "title": title,
                        "url": full_url
                    })

    # 防呆：如果沒有抓到任何項目
    if not items:
        items.append({"date": "", "title": "目前無新通報", "url": ""})

    return items
