from datetime import datetime, timezone
from app.data.news import fetch_raw_news


def _format_published(value) -> str:
    #Normalizes the published timestamp.
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return None


def get_market_news(limit: int = 15) -> dict:
    """
    Fetches raw headlines and shapes them into the NewsResponseSchema dict.
    """
    raw = fetch_raw_news(limit=limit)

    results = [
        {
            "title": item["title"],
            "link": item["link"],
            "publisher": item["publisher"],
            "published": _format_published(item["published"]),
        }
        for item in raw
    ]

    return {
        "count": len(results),
        "results": results
    }