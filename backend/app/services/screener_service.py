from app.data.universe import NIFTY_50
from app.data.fetch import batch_fetch_stocks
from app.analytics.indicators import calculate_indicators


def scan_universe(period: str = "6mo") -> dict:
    """
    Fetches data + calculates indicators for every stock in the
    NIFTY 50 universe. Returns {ticker: {price data + indicators}}.

    This is the foundation Week 2's filter engine will run on top of —
    scan_universe() gets the raw numbers, next week's filter functions
    decide which stocks pass a given screen (e.g. RSI < 30).
    """
    raw_data = batch_fetch_stocks(NIFTY_50, period=period)

    scanned = {}
    for ticker, data in raw_data.items():
        indicators = calculate_indicators(data["history"])
        scanned[ticker] = {
            "ticker": ticker,
            "current_price": data["current_price"],
            "change_percent": data["change_percent"],
            "volume": data["volume"],
            **indicators
        }

    return scanned