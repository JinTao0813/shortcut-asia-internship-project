import sqlite3
import faiss
import pickle
import numpy as np
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict
import os

from schemas import ReindexResponse, IndexStatus

router = APIRouter()

# Database and index paths
DB_PATH = os.path.join("database", "zus_coffee_internal.db")
FAISS_INDEX_PATH = os.path.join("data", "faiss_index.faiss")
META_PATH = os.path.join("data", "faiss_meta.pkl")

# ==================== Helper Functions ====================
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def reindex_embeddings_task(embed_model, faiss_index_path, meta_path, db_path):
    """
    Background task to regenerate embeddings from the database.
    This should be called after CRUD operations to keep the vector store in sync.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch all products and outlets
        cursor.execute("SELECT id, name, category, price, link FROM drinkware")
        products = cursor.fetchall()
        
        cursor.execute("SELECT id, name, category, address FROM outlets")
        outlets = cursor.fetchall()
        
        conn.close()
        
        # Prepare documents for embedding
        documents = []
        metadata = []
        
        # Process products
        for idx, product in enumerate(products):
            text = f"Product: {product['name']}, Category: {product['category']}, Price: {product['price']}"
            documents.append(text)
            metadata.append({
                "item_type": "drinkware",
                "item_index": idx,
                "text": text,
                "id": product['id']
            })
        
        # Process outlets
        for idx, outlet in enumerate(outlets):
            text = f"Outlet: {outlet['name']}, Region: {outlet['category']}, Address: {outlet['address']}"
            documents.append(text)
            metadata.append({
                "item_type": "outlet",
                "item_index": idx,
                "text": text,
                "id": outlet['id']
            })
        
        # Generate embeddings
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = embed_model.encode(documents, convert_to_numpy=True)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(embeddings)
        
        # Save FAISS index
        os.makedirs(os.path.dirname(faiss_index_path), exist_ok=True)
        faiss.write_index(index, faiss_index_path)
        
        # Save metadata
        with open(meta_path, "wb") as f:
            pickle.dump(metadata, f)
        
        # Update embedding_metadata table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM embedding_metadata")
        
        for idx, meta in enumerate(metadata):
            cursor.execute(
                "INSERT INTO embedding_metadata (item_type, item_index, text) VALUES (?, ?, ?)",
                (meta["item_type"], meta["item_index"], meta["text"])
            )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Reindexing complete. Total embeddings: {len(documents)}")
        return len(documents)
        
    except Exception as e:
        print(f"❌ Error during reindexing: {e}")
        import traceback
        traceback.print_exc()
        raise

# ==================== Endpoints ====================

@router.post("/reindex", response_model=ReindexResponse)
async def reindex_embeddings(background_tasks: BackgroundTasks, request: Request):
    """
    Regenerate all embeddings from the current database state.
    This should be called after creating, updating, or deleting products/outlets.
    """
    try:
        # Get the embedding model from app state
        ml_models = request.app.state.ml_models
        
        if "embed_model" not in ml_models:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")
        
        embed_model = ml_models["embed_model"]
        
        # Run reindexing synchronously (for now - can be made async)
        total = reindex_embeddings_task(embed_model, FAISS_INDEX_PATH, META_PATH, DB_PATH)
        
        # Reload the FAISS index into memory
        ml_models["faiss_index"] = faiss.read_index(FAISS_INDEX_PATH)
        with open(META_PATH, "rb") as f:
            ml_models["meta"] = pickle.load(f)
        
        return ReindexResponse(
            status="success",
            message="Embeddings regenerated successfully",
            total_embeddings=total
        )
        
    except Exception as e:
        print(f"Reindex error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error reindexing: {str(e)}")

@router.get("/status", response_model=IndexStatus)
async def get_index_status(request: Request):
    """
    Get the current status of the embedding index.
    """
    try:
        ml_models = request.app.state.ml_models
        
        faiss_exists = os.path.exists(FAISS_INDEX_PATH)
        meta_exists = os.path.exists(META_PATH)
        
        total_embeddings = 0
        if "faiss_index" in ml_models:
            total_embeddings = ml_models["faiss_index"].ntotal
        
        status = "ready" if (faiss_exists and meta_exists and total_embeddings > 0) else "not_initialized"
        
        return IndexStatus(
            status=status,
            total_embeddings=total_embeddings,
            faiss_index_exists=faiss_exists,
            meta_file_exists=meta_exists
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")
