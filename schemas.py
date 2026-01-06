from pydantic import BaseModel
from typing import Optional

class MetadataFilter(BaseModel):
    source: Optional[str] = None
    section: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    filters: Optional[MetadataFilter] = None
