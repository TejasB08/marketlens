from app.data.watchlist_store import watchlist_store, DEFAULT_USER
from app.data.fetch import batch_fetch_stocks
from app.analytics.indicators import calculate_indicators


def add_to_watchlist(ticker: str, user_id: str = DEFAULT_USER):
    watchlist_store.add(ticker, user_id)

def remove_from_watchlist(ticker: str, user_id: str = DEFAULT_USER):
    watchlist_store.remove(ticker, user_id)

def get_watchlist(user_id: str = DEFAULT_USER) -> dict:
    tickers = watchlist_store.get_all(user_id)
    raw_data = batch_fetch_stocks(tickers)

    results = {}
    for ticker, data in raw_data.items():
        indicators = calculate_indicators(data["history"])
        results[ticker] = {
            "ticker": ticker,
            "current_price": data["current_price"],
            "change_percent": data["change_percent"],
            "volume": data["volume"],
            **indicators
        }
    return results