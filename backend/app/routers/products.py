from fastapi import APIRouter, HTTPException, Request
from app.schemas import ProductQuery
from dependencies import llm
from pydantic import BaseModel
from typing import Optional
import json
import os

router = APIRouter()

# Path to products JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS_JSON_PATH = os.path.join(BASE_DIR, "data", "drinkware.json")

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: str
    category: str
    link: Optional[str] = None
    image_url: Optional[str] = None
    stock: int = 0

@router.post("/")
# Retrieve products from FAISS and generate summary
async def products_rag(payload: ProductQuery, request: Request):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    # Access models loaded in main.py lifespan
    models = request.app.state.ml_models
    if "embed_model" not in models or "faiss_index" not in models or "meta" not in models:
        raise HTTPException(status_code=503, detail="Search services not initialized")
    
    embed_model = models["embed_model"]
    faiss_index = models["faiss_index"]
    meta_store = models["meta"]

    try:
        # 1. Embed user query
        q_embedding = embed_model.encode([payload.query], convert_to_numpy=True)
        
        # 2. Search FAISS
        D, I = faiss_index.search(q_embedding, payload.top_k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            # Retrieve metadata (safe access)
            if idx < len(meta_store):
                doc_meta = meta_store[idx]
                hits.append({"score": float(score), "doc": doc_meta})

        if not hits:
            return {"query": payload.query, "summary": "No relevant products found.", "hits": []}

        # 3. Construct prompt for LLM summary
        docs_text = "\n\n---\n\n".join([
            f"Title: {h['doc'].get('name')}\n"
            f"Price: {h['doc'].get('price')}\n"
            f"Link: {h['doc'].get('link')}\n"
            f"Description: {h['doc'].get('category', '')}" 
            for h in hits
        ])

        prompt = (
            "You are an assistant that summarizes product information for a user.\n"
            "Given the following top-matching product documents from a product catalog, "
            "provide a concise summary emphasizing the best matches for the user's query "
            "and include any direct product links.\n\n"
            f"User query: {payload.query}\n\n"
            "Documents:\n"
            f"{docs_text}\n\n"
            "Return a short (3-5 sentence) recommendation/summary focusing on what matches the query best. "
            "Also include a short bullet list of the matched product names and links."
        )

        # 4. Generate Summary using shared LLM
        summary_response = llm.invoke(prompt)
        summary_text = summary_response.content

        return {
            "query": payload.query, 
            "summary": summary_text.strip(), 
            "hits": hits
        }

    except Exception as e:
        # Log error here in a real app
        raise HTTPException(status_code=500, detail=f"RAG processing error: {str(e)}")

# CRUD Endpoints for Admin Dashboard
def read_products_file():
    """Read products from JSON file"""
    try:
        with open(PRODUCTS_JSON_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading products file: {str(e)}")

def write_products_file(products):
    """Write products to JSON file"""
    try:
        with open(PRODUCTS_JSON_PATH, 'w') as f:
            json.dump(products, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing products file: {str(e)}")

@router.get("/all", response_model=list)
def get_all_products():
    """Get all products from the JSON file"""
    products = read_products_file()
    # Ensure each product has an id
    for i, product in enumerate(products):
        if 'id' not in product:
            product['id'] = i + 1
    return products

@router.post("/create")
def create_product(product: Product):
    """Create a new product"""
    products = read_products_file()
    # Generate new ID
    new_id = max([p.get('id', 0) for p in products], default=0) + 1
    new_product = {"id": new_id, **product.dict(exclude={'id'})}
    products.append(new_product)
    write_products_file(products)
    return new_product

@router.put("/{product_id}")
def update_product(product_id: int, product: Product):
    """Update an existing product"""
    products = read_products_file()
    for i, p in enumerate(products):
        if p.get('id') == product_id:
            products[i] = {"id": product_id, **product.dict(exclude={'id'})}
            write_products_file(products)
            return products[i]
    raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{product_id}")
def delete_product(product_id: int):
    """Delete a product"""
    products = read_products_file()
    products = [p for p in products if p.get('id') != product_id]
    write_products_file(products)
    return {"message": "Product deleted successfully"}