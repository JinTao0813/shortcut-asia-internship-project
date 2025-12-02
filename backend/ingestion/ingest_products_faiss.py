import os
import json
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DATA_DIR = "backend/data"
DRINKWARE_JSON = os.path.join(DATA_DIR, "drinkware.json")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.faiss")
META_PATH = os.path.join(DATA_DIR, "faiss_meta.pkl")

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"  # good general-purpose model

def load_documents():
    with open(DRINKWARE_JSON, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return docs

def build_faiss_index(docs):
    model = SentenceTransformer(EMBED_MODEL)

    texts = []
    metas = []
    for d in docs:
        text = " | ".join(filter(None, [d.get("name"), d.get("description", ""), d.get("price", ""), d.get("link")]))
        texts.append(text)
        metas.append(d) 

    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize vectors (optional but common)
    # faiss.normalize_L2(embeddings)  # optional if you want cosine via inner product

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)  # L2 (works well). For cosine you can normalize and use IndexFlatIP.
    index.add(embeddings)

    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(metas, f)

    print(f"Built FAISS index with {index.ntotal} vectors. Saved to {FAISS_INDEX_PATH}")

if __name__ == "__main__":
    docs = load_documents()
    build_faiss_index(docs)
