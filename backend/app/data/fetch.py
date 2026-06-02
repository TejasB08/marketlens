import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str, period: str = "6mo") -> dict:
    """
    Fetches stock data from yfinance.
    ticker: e.g. "RELIANCE.NS"
    period: how much history to fetch e.g. "1mo", "6mo", "1y"
    """
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

        return {
            "ticker": ticker,
            "current_price": current_price,
            "previous_close": previous_close,
            "change_percent": round(change_percent, 2) if change_percent else None,
            "volume": volume,
            "history": history  # this is a pandas DataFrame
        }

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None