from app.data.fetch import get_stock_data
from app.analytics.indicators import calculate_indicators
from app.schemas.quote_schema import QuoteSchema, IndicatorsSchema


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