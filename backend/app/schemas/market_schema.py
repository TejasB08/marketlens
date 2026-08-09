from pydantic import BaseModel
from typing import Optional, List


class MoverStockSchema(BaseModel):
    ticker: str
    current_price: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]


class TopMoversSchema(BaseModel):
    gainers: List[MoverStockSchema]
    losers: List[MoverStockSchema]


class SectorBreakdownSchema(BaseModel):
    sector: str
    avg_change_percent: float
    stock_count: int