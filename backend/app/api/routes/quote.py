from fastapi import APIRouter, HTTPException
from app.services.market_service import get_market_overview, get_quote
from app.schemas.quote_schema import QuoteSchema
from app.services.market_service import get_quote
from app.data.fetch import get_stock_data

router = APIRouter()


@router.get("/quote/{ticker}", response_model=QuoteSchema)
def fetch_quote(ticker: str):
    """
    GET /quote/RELIANCE.NS
    Returns price data and technical indicators for a stock.
    """
    # Uppercase the ticker just in case user sends lowercase
    ticker = ticker.upper()

    result = get_quote(ticker)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch data for ticker: {ticker}"
        )

    return result

@router.get("/market/overview")
def market_overview():
    """
    GET /market/overview
    Returns NIFTY, BANKNIFTY and SENSEX overview.
    """
    result = get_market_overview()

    if not result:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch market overview"
        )

    return result

@router.get("/quote/{ticker}/history")
def fetch_history(ticker: str):
    """
    GET /quote/RELIANCE.NS/history
    Returns 6 months of daily closing prices for charting.
    """
    ticker = ticker.upper()
    raw_data = get_stock_data(ticker)

    if raw_data is None:
        raise HTTPException(status_code=404, detail=f"Ticker not found: {ticker}")

    history = raw_data["history"]

    # Convert DataFrame to list of {date, close} objects
    chart_data = []
    for date, row in history.iterrows():
        chart_data.append({
            "date": str(date)[:10],  # Just the YYYY-MM-DD part
            "close": round(float(row["Close"]), 2)
        })

    return chart_data