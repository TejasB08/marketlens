from pydantic import BaseModel
from typing import List
from app.schemas.screener_schema import ScreenerStockSchema


class WatchlistResponseSchema(BaseModel):
    """Reuses ScreenerStockSchema since a watchlist entry needs the
    same price + indicator fields a screener row already has."""
    count: int
    tickers: List[ScreenerStockSchema]