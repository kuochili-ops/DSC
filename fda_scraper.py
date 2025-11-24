
import feedparser
import re

def extract_drug_info(title):
    # 抽取藥品名稱與主成分
    brand_match = re.search(r"taking\s+([A-Za-z0-9]+)", title)
    ingredient_match = re.search(r"\((.*?)\)", title)
    brand = brand_match.group(1) if brand_match else ""
    ingredient = ingredient_match.group(1) if ingredient_match else ""
    return brand, ingredient

def get_latest_communications():
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    feed = feedparser.parse(rss_url)

    items = []
    for entry in feed.entries:
        brand, ingredient = extract_drug_info(entry.title)
        items.append({
            "date": entry.published,
            "title": entry.title,
            "brand": brand,
            "ingredient": ingredient,
            "url": entry.link
        })

    if not items:
        items.append({"date": "", "title": "目前無新通報", "brand": "", "ingredient": "", "url": ""})

    return items
