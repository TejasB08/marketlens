import yfinance as yf
import pandas as pd
from app.utils.cache import stock_cache


def get_stock_data(ticker: str, period: str = "6mo") -> dict:
    """
    Fetches stock data from yfinance.
    ticker: e.g. "RELIANCE.NS"
    period: how much history to fetch e.g. "1mo", "6mo", "1y"
    """
    cache_key = f"{ticker}_{period}"
    cached = stock_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        stock = yf.Ticker(ticker)

        # Current price info
        info = stock.info
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")
        volume = info.get("volume")

        # Calculate change percent
        if current_price and previous_close:
            change_percent = ((current_price - previous_close) / previous_close) * 100
        else:
            change_percent = None

        # Historical OHLCV data for charts and indicators
        history = stock.history(period=period)

        if history.empty:
            return None

        result = {
            "ticker": ticker,
            "current_price": current_price,
            "previous_close": previous_close,
            "change_percent": round(change_percent, 2) if change_percent else None,
            "volume": volume,
            "history": history  # this is a pandas DataFrame
        }

        stock_cache.set(cache_key, result)
        return result

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def batch_fetch_stocks(tickers: list, period: str = "6mo") -> dict:
    """
    Fetches data for multiple tickers by looping over get_stock_data.
    Returns {ticker: data_dict}. Tickers that fail to fetch are
    silently skipped rather than crashing the whole scan.

    Cached tickers resolve instantly, so a rescan after tweaking a
    filter is fast even though this is a plain loop, not parallel.
    """
    results = {}
    for ticker in tickers:
        data = get_stock_data(ticker, period=period)
        if data is not None:
            results[ticker] = data
    return results