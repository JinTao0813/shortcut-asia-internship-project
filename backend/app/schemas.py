from pydantic import BaseModel
from typing import Optional

class NLQuery(BaseModel):
    query: str
    max_rows: Optional[int] = 50

class ProductQuery(BaseModel):
    query: str
    top_k: Optional[int] = 4