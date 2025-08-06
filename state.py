from typing import List, Dict
from pydantic import BaseModel,Field


class Article(BaseModel):
    title: str
    url: str
    content: str

#-- Define Langraph State --
class NewsAgentState(BaseModel):
    topic: str
    sources: List[str]
    articles: List[Article] = Field(default_factory=list)
    summaries: List[str] = []