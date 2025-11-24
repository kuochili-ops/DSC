
import feedparser

def get_latest_communications():
    """
    使用 FDA 官方 RSS Feed 擷取最新藥品安全通訊
    回傳格式：
    [
        {
            "date": "Fri, 16 May 2025 10:00:00 EST",
            "title": "FDA requires warning about rare but severe itching...",
            "url": "https://www.fda.gov/drugs/drug-safety-and-availability/..."
        },
        ...
    ]
    """
    rss_url = "https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-communications"
    feed = feedparser.parse(rss_url)

    items = []
    for entry in feed.entries:
        items.append({
            "date": entry.published,
            "title": entry.title,
            "url": entry.link
        })

    if not items:
        items.append({"date": "", "title": "目前無新通報", "url": ""})

    return items

# 測試
if __name__ == "__main__":
    data = get_latest_communications()
    for item in data[:5]:
        print(item)
