from pydantic import BaseModel
from typing import Optional, List


class ScreenerStockSchema(BaseModel):
    """One stock's price + indicators, as returned by a screener scan."""
    ticker: str
    current_price: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    rsi: Optional[float]
    ema20: Optional[float]
    ema50: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]


class ScreenerResponseSchema(BaseModel):
    """Response shape for a full scan or a preset screen run."""
    preset: Optional[str] = None
    count: int
    results: List[ScreenerStockSchema]