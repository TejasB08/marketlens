from pydantic import BaseModel
from typing import Optional, List


class NewsItemSchema(BaseModel):
    title: str
    link: Optional[str] = None
    publisher: Optional[str] = None
    published: Optional[str] = None


class NewsResponseSchema(BaseModel):
    count: int
    results: List[NewsItemSchema]