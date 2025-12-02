from fastapi import APIRouter, HTTPException, Request
from app.schemas import ProductQuery
from dependencies import llm

router = APIRouter()

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