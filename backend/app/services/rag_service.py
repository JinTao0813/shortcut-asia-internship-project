from fastapi import HTTPException

class RAGService:
    def __init__(self, llm):
        self.llm = llm

    def search_and_summarize(self, query: str, top_k: int, ml_models: dict):
        # 1. Validate that the models are loaded
        if "embed_model" not in ml_models or "faiss_index" not in ml_models or "meta" not in ml_models:
            raise HTTPException(status_code=503, detail="AI Search services are not initialized.")

        embed_model = ml_models["embed_model"]
        faiss_index = ml_models["faiss_index"]
        meta_store = ml_models["meta"]

        try:
            # 2. Do embedding on the user's query
            q_embedding = embed_model.encode([query], convert_to_numpy=True)

            # 3. Search FAISS
            # D = distances (scores), I = indices
            D, I = faiss_index.search(q_embedding, top_k)

            hits = []
            for score, idx in zip(D[0], I[0]):
                if idx == -1: continue # FAISS returns -1 if not enough neighbors found
                
                # Safe access to metadata
                if idx < len(meta_store):
                    doc_meta = meta_store[idx]
                    hits.append({"score": float(score), "doc": doc_meta})

            # 4. Handle no results
            if not hits:
                return {
                    "query": query,
                    "summary": "I couldn't find any products matching your description.",
                    "hits": []
                }

            # 5. Construct prompt for LLM
            docs_context = "\n\n".join([
                f"Product: {h['doc'].get('name')}\n"
                f"Price: {h['doc'].get('price')}\n"
                f"Link: {h['doc'].get('link')}\n"
                f"Description: {h['doc'].get('category', '')}" 
                for h in hits
            ])

            prompt = (
                f"You are a helpful shopping assistant for ZUS Coffee.\n"
                f"User Request: {query}\n\n"
                f"Here are the top matching products from our catalog:\n"
                f"{docs_context}\n\n"
                f"Task: Write a helpful, enthusiastic summary recommending these products to the user. "
                f"Keep it under 4 sentences. Mention the product names and prices explicitly."
            )

            # 6. Call the LLM
            summary_response = self.llm.invoke(prompt)
            # Handle LangChain response variations (string vs object)
            summary_text = summary_response.content if hasattr(summary_response, "content") else str(summary_response)

            return {
                "query": query,
                "summary": summary_text.strip(),
                "hits": hits
            }

        except Exception as e:
            # Log the actual error internally if you have a logger
            print(f"RAG Service Error: {e}")
            raise HTTPException(status_code=500, detail="Internal error processing product search.")