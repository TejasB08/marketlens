from pydantic import BaseModel
from typing import Optional


class IndicatorsSchema(BaseModel):
    rsi: Optional[float] = None
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None


class QuoteSchema(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    indicators: IndicatorsSchema