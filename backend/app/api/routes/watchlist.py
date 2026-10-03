from fastapi import APIRouter
from app.services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
)
from app.schemas.watchlist_schema import WatchlistResponseSchema

router = APIRouter()


@router.get("/watchlist", response_model=WatchlistResponseSchema)
def view_watchlist():
    """
    GET /watchlist
    Returns live price + indicator data for every watchlisted ticker.
    """
    results = get_watchlist()
    return {
        "count": len(results),
        "tickers": list(results.values())
    }


@router.post("/watchlist/{ticker}")
def add_ticker(ticker: str):
    """
    POST /watchlist/RELIANCE.NS
    Adds a ticker to the watchlist.
    """
    ticker = ticker.upper()
    add_to_watchlist(ticker)
    return {"message": f"{ticker} added to watchlist"}


@router.delete("/watchlist/{ticker}")
def remove_ticker(ticker: str):
    """
    DELETE /watchlist/RELIANCE.NS
    Removes a ticker from the watchlist.
    """
    ticker = ticker.upper()
    remove_from_watchlist(ticker)
    return {"message": f"{ticker} removed from watchlist"}