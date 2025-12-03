import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
from dependencies import DATABASE_PATH, FAISS_INDEX_PATH, EMBEDDING_MODEL

# -------------------- Config --------------------
TOP_K_DEFAULT = 5

# -------------------- RAG Service --------------------
class RAGService:
    def __init__(self, llm=None):
        self.llm = llm
        # Load embedding model
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        # Load FAISS index
        try:
            self.faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index: {e}")

    # -------------------- Helper: Retrieve metadata --------------------
    def get_metadata(self, indices):
        """
        Fetch metadata from SQLite embedding_metadata table for given FAISS indices.
        Returns a list of dicts corresponding to each index.
        """
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        metadata = []
        for idx in indices:
            if idx == -1:  # invalid FAISS index
                metadata.append(None)
                continue
            
            # Convert numpy.int64 to Python int for SQLite compatibility
            db_id = int(idx + 1)  # SQLite AUTOINCREMENT IDs start at 1
            
            cursor.execute(
                "SELECT item_type, item_index, text FROM embedding_metadata WHERE id=?",
                (db_id,)
            )
            row = cursor.fetchone()
            
            if row:
                metadata.append({
                    "item_type": row[0],
                    "item_index": row[1],
                    "text": row[2]
                })
            else:
                metadata.append(None)
        conn.close()
        return metadata

    # -------------------- Helper: Extract LLM response --------------------
    def extract_llm_content(self, response):
        """
        Extract text content from LLM response in various formats.
        Handles Claude's list format, LangChain's AIMessage, and simple strings.
        """
        if hasattr(response, 'content'):
            content = response.content
            
            # Handle list format (Claude/Anthropic)
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif isinstance(item, str):
                        text_parts.append(item)
                return ' '.join(text_parts).strip()
            else:
                return str(content)
        elif isinstance(response, dict):
            content = response.get('content', '')
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                return ' '.join(text_parts).strip()
            else:
                return str(content)
        else:
            return str(response)

    # -------------------- Search and summarize --------------------
    def search_and_summarize(self, query: str, top_k: int = TOP_K_DEFAULT, llm=None):
        """
        Main RAG function:
        1. Embed user query
        2. Search FAISS index
        3. Retrieve metadata
        4. Construct context and prompt
        5. Call LLM
        """
        try:
            # 1. Generate query embedding
            q_embedding = self.embed_model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(q_embedding)

            # 2. Search FAISS
            D, I = self.faiss_index.search(q_embedding, top_k)
            hits_meta = self.get_metadata(I[0])

            # 3. Construct hits and context
            hits = []
            context_pieces = []
            for score, meta in zip(D[0], hits_meta):
                if meta is None:
                    continue
                # Different handling for drinkware vs outlets
                if meta["item_type"] == "drinkware":
                    context = meta["text"]  # text already contains name, category, price
                elif meta["item_type"] == "outlet":
                    context = meta["text"]  # text already contains name, region, address
                else:
                    context = meta["text"]
                hits.append({"score": float(score), "doc": meta, "context": context})
                context_pieces.append(context)

            if not hits:
                return {
                    "query": query,
                    "summary": "I couldn't find any matching products or outlets.",
                    "hits": []
                }

            # 4. Construct prompt for LLM
            docs_context = "\n\n".join(context_pieces)
            prompt = (
                f"You are a helpful assistant for ZUS Coffee internal operations.\n"
                f"User Request: {query}\n\n"
                f"Here are the top relevant entries from our database:\n"
                f"{docs_context}\n\n"
                f"Task: Provide a concise, clear, and helpful summary to the user. "
                f"Include the names, prices (if available), and addresses or links where applicable."
            )

            # 5. Call LLM
            llm_to_use = llm or self.llm
            if llm_to_use is None:
                summary_text = "LLM not configured. Context retrieved:\n" + docs_context
            else:
                summary_response = llm_to_use.invoke(prompt)
                # Extract content using helper method
                summary_text = self.extract_llm_content(summary_response)

            return {
                "query": query,
                "summary": summary_text.strip(),
                "hits": hits
            }

        except Exception as e:
            print(f"RAG Service Error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Internal error processing the query.")