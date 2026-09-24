from fastapi import APIRouter, HTTPException
from app.services.news_service import get_market_news
from app.schemas.news_schema import NewsResponseSchema

router = APIRouter()


@router.get("/news", response_model=NewsResponseSchema)
def market_news(limit: int = 15):
    """
    GET /api/v1/news?limit=15
    Returns recent headlines only (title, source, link, date)
    """
    result = get_market_news(limit=limit)

    if not result["results"]:
        raise HTTPException(status_code=503, detail="Could not fetch market news")

    return result