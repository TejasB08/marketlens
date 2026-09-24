import yfinance as yf
from app.utils.cache import SimpleCache

# Separate cache instance (same SimpleCache used for stock data) to avoid polluting stock data cache with news items.
news_cache = SimpleCache(ttl_seconds=600)

# Tickers whose Yahoo Finance news feed we pull from.
# Keep this list short — every ticker here is a separate news fetch.
NEWS_SOURCE_TICKERS = ["^NSEI", "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]


def _extract_fields(entry: dict) -> dict:
    """
    Extracts relevant fields from a raw news entry returned by yfinance.
    NOTE: if headlines come back empty, this is the first place to check —
    print(entry) for one raw item and adjust the key lookups below to match
    whatever version of yfinance is installed.
    """
    content = entry.get("content", entry)

    title = content.get("title")

    link = content.get("link")
    canonical = content.get("canonicalUrl")
    if isinstance(canonical, dict):
        link = canonical.get("url") or link

    publisher = content.get("publisher")
    provider = content.get("provider")
    if isinstance(provider, dict):
        publisher = provider.get("displayName") or publisher

    published = content.get("providerPublishTime") or content.get("pubDate")

    return {
        "title": title,
        "link": link,
        "publisher": publisher,
        "published": published,
    }


def fetch_raw_news(limit: int = 15) -> list:
    """
    Fetches recent news across NEWS_SOURCE_TICKERS, dedupes by headline,
    sorts newest first, and returns at most `limit` items as plain dicts.
    """
    cache_key = f"raw_news_{limit}"
    cached = news_cache.get(cache_key)
    if cached is not None:
        return cached

    seen_titles = set()
    items = []

    for ticker in NEWS_SOURCE_TICKERS:
        try:
            raw = yf.Ticker(ticker).news or []
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
            continue

        for entry in raw:
            fields = _extract_fields(entry)
            title = fields["title"]
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            items.append(fields)

    # Sort newest first. Missing timestamps sort last rather than crashing.
    items.sort(key=lambda i: i["published"] or 0, reverse=True)

    result = items[:limit]
    news_cache.set(cache_key, result)
    return result