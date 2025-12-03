from pydantic import BaseModel
from typing import Optional, List

# ==================== Legacy Schemas ====================
class NLQuery(BaseModel):
    query: str
    max_rows: Optional[int] = 50

class ProductQuery(BaseModel):
    query: str
    top_k: Optional[int] = 4

# ==================== Product Schemas ====================
class ProductBase(BaseModel):
    name: str
    link: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

# ==================== Outlet Schemas ====================
class OutletBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    maps_url: Optional[str] = None

class OutletCreate(OutletBase):
    pass

class OutletUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    maps_url: Optional[str] = None

class Outlet(OutletBase):
    id: int

    class Config:
        from_attributes = True

# ==================== Chat Schemas ====================
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    session_id: str

# ==================== Embedding Schemas ====================
class ReindexResponse(BaseModel):
    status: str
    message: str
    total_embeddings: int

class IndexStatus(BaseModel):
    status: str
    total_embeddings: int
    faiss_index_exists: bool
    meta_file_exists: bool