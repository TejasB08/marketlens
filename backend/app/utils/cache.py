import time


class SimpleCache:
    """
    Minimal in-memory cache with time-based expiry (TTL).

    Why: the screener will call get_stock_data() ~50 times per scan.
    Without caching, tweaking one filter and re-scanning means
    re-hitting yfinance for all 50 tickers again immediately.
    This cache lets repeated scans within the TTL window reuse
    already-fetched data instead.
    """

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.store = {}  # key -> (timestamp, value)

    def get(self, key: str):
        entry = self.store.get(key)
        if entry is None:
            return None

        timestamp, value = entry
        if time.time() - timestamp > self.ttl:
            del self.store[key]  # expired, evict it
            return None

        return value

    def set(self, key: str, value):
        self.store[key] = (time.time(), value)


# Single shared instance imported by fetch.py.
# 300s = 5 min TTL — long enough to avoid hammering yfinance while
# a user tweaks filters, short enough that prices don't go stale.
stock_cache = SimpleCache(ttl_seconds=300)