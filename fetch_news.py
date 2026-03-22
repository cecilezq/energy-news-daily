import feedparser
import json
import datetime
import os
import re

FEEDS = {
    "global": [
        {"url": "https://www.pv-magazine.com/feed/"},
        {"url": "https://www.pvtech.org/feed/"},
        {"url": "https://cleantechnica.com/feed/"},
        {"url": "https://reneweconomy.com.au/feed/"},
        {"url": "https://electrek.co/feed/"},
    ],
    "southeast_asia": [
        {"url": "https://www.pv-magazine-asia.com/feed/"},
        {"url": "https://news.google.com/rss/search?q=renewable+energy+solar+wind+storage+southeast+asia+vietnam+thailand+indonesia+malaysia+philippines&hl=en-US&gl=US&ceid=US:en"},
    ],
    "china": [
        {"url": "https://news.google.com/rss/search?q=china+solar+wind+storage+renewable+energy+new+energy&hl=en-US&gl=US&ceid=US:en"},
    ],
    "major_events": [
        {"url": "https://news.google.com/rss/search?q=renewable+energy+gigawatt+billion+investment+policy+record+milestone&hl=en-US&gl=US&ceid=US:en"},
    ],
}

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:300]

def fetch_feed(url, max_items=10):
    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
        items = []
        for entry in feed.entries[:max_items]:
            published = entry.get("published", "")
            try:
                parsed_time = entry.get("published_parsed")
                if parsed_time:
                    published = datetime.datetime(*parsed_time[:6]).strftime("%Y-%m-%d")
            except Exception:
                pass

            item = {
                "title": clean_html(entry.get("title", "")),
                "link": entry.get("link", ""),
                "summary": clean_html(entry.get("summary", "")),
                "published": published,
                "source": clean_html(feed.feed.get("title", "")),
            }
            if item["title"] and item["link"]:
                items.append(item)
        return items
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        key = item["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def main():
    data = {
        "updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "sections": {},
    }

    for section, feeds in FEEDS.items():
        items = []
        for feed_info in feeds:
            fetched = fetch_feed(feed_info["url"])
            items.extend(fetched)
        items = deduplicate(items)
        data["sections"][section] = items[:15]

    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in data["sections"].values())
    print(f"Done. {total} articles saved. Updated at {data['updated']}")

if __name__ == "__main__":
    main()
