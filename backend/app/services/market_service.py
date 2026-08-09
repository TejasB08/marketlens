from app.data.fetch import get_stock_data
from app.analytics.indicators import calculate_indicators
from app.schemas.quote_schema import QuoteSchema, IndicatorsSchema
from app.services.screener_service import scan_universe
from app.data.universe import SECTOR_MAP

def get_quote(ticker: str) -> QuoteSchema:
    """
    Main service function.
    Fetches stock data, calculates indicators,
    and returns a clean QuoteSchema object.
    """

    # Step 1: Fetch raw data from yfinance
    raw_data = get_stock_data(ticker)

    if raw_data is None:
        return None

    # Step 2: Calculate indicators from history
    indicators_data = calculate_indicators(raw_data["history"])

    # Step 3: Build and return the schema
    return QuoteSchema(
        ticker=raw_data["ticker"],
        current_price=raw_data["current_price"],
        previous_close=raw_data["previous_close"],
        change_percent=raw_data["change_percent"],
        volume=raw_data["volume"],
        indicators=IndicatorsSchema(**indicators_data)
    )

def get_market_overview() -> dict:
    """
    Returns overview of major Indian market indices.
    """
    indices = {
        "NIFTY_50": "^NSEI",
        "BANK_NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN"
    }

    overview = {}

    for name, symbol in indices.items():
        data = get_stock_data(symbol, period="5d")
        if data:
            overview[name] = {
                "current_price": data["current_price"],
                "change_percent": data["change_percent"],
                "volume": data["volume"]
            }

    return overview

def get_top_movers(limit: int = 5) -> dict:
    """
    Returns top N gainers and top N losers across the NIFTY 50,
    ranked by change_percent. Reuses scan_universe() so this is
    cache-backed just like the screener — cheap on repeat calls.
    """
    scanned = scan_universe()

    # Filter out any stocks where change_percent came back None
    # (e.g. a ticker yfinance couldn't compute previous_close for)
    valid = [s for s in scanned.values() if s["change_percent"] is not None]

    ranked = sorted(valid, key=lambda s: s["change_percent"], reverse=True)

    return {
        "gainers": ranked[:limit],
        "losers": ranked[-limit:][::-1]  # reverse so biggest loser is first
    }


def get_sector_breakdown() -> list:
    """
    Groups NIFTY 50 stocks by sector and returns each sector's
    average change_percent, sorted best-performing first.
    """
    scanned = scan_universe()

    sector_totals = {}  # sector -> list of change_percent values

    for ticker, stock in scanned.items():
        sector = SECTOR_MAP.get(ticker, "Other")
        if stock["change_percent"] is not None:
            sector_totals.setdefault(sector, []).append(stock["change_percent"])

    breakdown = [
        {
            "sector": sector,
            "avg_change_percent": round(sum(values) / len(values), 2),
            "stock_count": len(values)
        }
        for sector, values in sector_totals.items()
    ]

    return sorted(breakdown, key=lambda s: s["avg_change_percent"], reverse=True)