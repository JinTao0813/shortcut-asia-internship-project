"""
Build FAISS embeddings index from database
Run this script to create/rebuild the embeddings index

This script:
1. Reads product and outlet data directly from the SQLite database
2. Generates embeddings using sentence-transformers
3. Creates a FAISS index for vector similarity search
4. Saves the index and metadata for the RAG system
"""
import os
import sys
import sqlite3
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Add parent directory to path to import dependencies
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from dependencies
try:
    from dependencies import DATABASE_PATH, FAISS_INDEX_PATH, PKL_PATH, META_PATH, EMBEDDING_MODEL
    META_PATH = "data/faiss_meta.pkl"  # Define if not in dependencies
    EMBEDDING_MODEL = EMBEDDING_MODEL
except ImportError:
    # Fallback to hardcoded paths if dependencies not found
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "zus_coffee_internal.db")
    FAISS_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "zus_embeddings.index")
    PKL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "zus_embeddings.pkl")
    META_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faiss_meta.pkl")
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

def build_embeddings():
    """Build FAISS index from database"""
    
    print("=" * 60)
    print("Building FAISS Embeddings Index from Database")
    print("=" * 60)
    
    # 1. Load embedding model
    print("\n1. Loading embedding model...")
    embed_model = SentenceTransformer(EMBEDDING_MODEL)
    print("   ✓ Model loaded")
    
    # 2. Connect to database
    print("\n2. Connecting to database...")
    if not os.path.exists(DATABASE_PATH):
        print(f"   ✗ Database not found at: {DATABASE_PATH}")
        print("   Please run ingest_scraped_data_to_sqlite.py first!")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 3. Fetch products (drinkware)
    print("\n3. Fetching products (drinkware) from database...")
    cursor.execute("SELECT id, name, category, price FROM drinkware")
    products = cursor.fetchall()
    print(f"   ✓ Found {len(products)} products")
    
    # 4. Fetch outlets
    print("\n4. Fetching outlets from database...")
    cursor.execute("SELECT id, name, category, address FROM outlets")
    outlets = cursor.fetchall()
    print(f"   ✓ Found {len(outlets)} outlets")
    
    conn.close()
    
    if len(products) == 0 and len(outlets) == 0:
        print("\n   ✗ No data found in database!")
        print("   Please run ingest_scraped_data_to_sqlite.py first!")
        return
    
    # 5. Prepare texts and metadata
    print("\n5. Preparing texts for embedding...")
    texts = []
    metadata = []
    
    # Add products
    for prod_id, name, category, price in products:
        text = f"Product: {name}, Category: {category or 'N/A'}, Price: RM{price or 'N/A'}"
        texts.append(text)
        metadata.append({
            "item_type": "drinkware",
            "item_index": prod_id,
            "text": text
        })
    
    # Add outlets
    for out_id, name, category, address in outlets:
        text = f"Outlet: {name}, Category: {category or 'N/A'}, Address: {address or 'N/A'}"
        texts.append(text)
        metadata.append({
            "item_type": "outlet",
            "item_index": out_id,
            "text": text
        })
    
    print(f"   ✓ Prepared {len(texts)} texts for embedding")
    
    # 6. Generate embeddings
    print(f"\n6. Generating embeddings (this may take a minute)...")
    embeddings = embed_model.encode(
        texts, 
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32
    )
    print(f"   ✓ Generated {len(embeddings)} embeddings")
    print(f"   ✓ Embedding dimension: {embeddings.shape[1]}")
    
    # 7. Normalize for cosine similarity
    print("\n7. Normalizing embeddings for cosine similarity...")
    faiss.normalize_L2(embeddings)
    print("   ✓ Normalized")
    
    # 8. Create FAISS index
    print("\n8. Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity after normalization)
    index.add(embeddings)
    print(f"   ✓ Index created with {index.ntotal} vectors")
    
    # 9. Save FAISS index
    print("\n9. Saving FAISS index...")
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"   ✓ Saved to: {FAISS_INDEX_PATH}")
    
    # 10. Save metadata (for compatibility)
    print("\n10. Saving metadata...")
    os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"   ✓ Saved to: {META_PATH}")
    
    # 11. Save pickle file (legacy format)
    print("\n11. Saving pickle file (legacy format)...")
    os.makedirs(os.path.dirname(PKL_PATH), exist_ok=True)
    with open(PKL_PATH, "wb") as f:
        pickle.dump({
            "texts": texts,
            "metadata": metadata,
            "embeddings": embeddings
        }, f)
    print(f"   ✓ Saved to: {PKL_PATH}")
    
    # 12. Update embedding_metadata table in database
    print("\n12. Updating database embedding_metadata table...")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embedding_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_type TEXT,
        item_index INTEGER,
        text TEXT
    )
    """)
    
    # Clear old metadata
    cursor.execute("DELETE FROM embedding_metadata")
    
    # Insert new metadata
    for idx, meta in enumerate(metadata):
        cursor.execute(
            "INSERT INTO embedding_metadata (id, item_type, item_index, text) VALUES (?, ?, ?, ?)",
            (idx + 1, meta["item_type"], meta["item_index"], meta["text"])
        )
    
    conn.commit()
    conn.close()
    print(f"   ✓ Updated {len(metadata)} entries in database")
    
    # 13. Test the index
    print("\n13. Testing the index with sample query...")
    test_query = "coffee tumbler"
    test_embedding = embed_model.encode([test_query], convert_to_numpy=True)
    faiss.normalize_L2(test_embedding)
    D, I = index.search(test_embedding, 3)
    
    print(f"\n   Test query: '{test_query}'")
    print(f"   Top 3 results:")
    for i, (dist, idx) in enumerate(zip(D[0], I[0])):
        if idx < len(metadata):
            print(f"   {i+1}. Score: {dist:.4f} - {metadata[idx]['text'][:70]}...")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ EMBEDDINGS BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nTotal items indexed: {len(texts)}")
    print(f"  - Products: {len(products)}")
    print(f"  - Outlets: {len(outlets)}")
    print(f"\nFiles created:")
    print(f"  - {FAISS_INDEX_PATH}")
    print(f"  - {META_PATH}")
    print(f"  - {PKL_PATH}")
    print(f"\nDatabase table updated:")
    print(f"  - embedding_metadata ({len(metadata)} entries)")
    print("\n🚀 Your RAG system is now ready to use!")
    print("   Restart your FastAPI server to load the new embeddings.")
    print()

if __name__ == "__main__":
    try:
        build_embeddings()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
