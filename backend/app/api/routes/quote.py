from fastapi import APIRouter, HTTPException
from app.services.market_service import get_market_overview, get_quote
from app.schemas.quote_schema import QuoteSchema

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