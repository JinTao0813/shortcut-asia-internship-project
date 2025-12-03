import os
import pickle
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss

from routers import products, outlets, food, drinks, chat, embeddings, admin
from dependencies import DATA_DIR, DATABASE_DIR, DATABASE_PATH, OUTLETS_JSON, DRINKWARE_JSON, PKL_PATH, META_PATH, EMBEDDING_MODEL, FAISS_INDEX_PATH

# Global dictionary to hold ML models
ml_models = {}

# ==============================
# Lifespan context manager (replaces deprecated on_event)
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models
    try:
        print("Loading SentenceTransformer model...")
        ml_models["embed_model"] = SentenceTransformer(EMBEDDING_MODEL)
        print("SentenceTransformer loaded.")

        # Define paths relative to backend directory
        faiss_index_path = FAISS_INDEX_PATH
        meta_path = META_PATH

        if os.path.exists(faiss_index_path):
            ml_models["faiss_index"] = faiss.read_index(faiss_index_path)
            print("FAISS index loaded.")
        else:
            print(f"⚠️ FAISS index not found at {faiss_index_path}")

        if os.path.exists(meta_path):
            with open(meta_path, "rb") as f:
                ml_models["meta"] = pickle.load(f)
            print("Meta loaded.")
        else:
            print(f"⚠️ Meta file not found at {meta_path}")

        print("✅ All models loaded successfully.")

    except Exception as e:
        print(f"❌ Error loading ML models: {e}")
        import traceback
        traceback.print_exc()

    yield  # Application runs here

    # Shutdown: Cleanup (optional)
    ml_models.clear()
    print("🔄 ML models cleared from memory.")

# ==============================
# FastAPI app setup with lifespan
# ==============================
app = FastAPI(
    title="ZUS Coffee Internal Assistant API",
    description="API for managing ZUS Coffee products, outlets, and AI assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Attach the ml_models dict to app state
app.state.ml_models = ml_models

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React/Next.js dev
        "http://localhost:5173",  # Vite dev
        "http://localhost:8000",  # Backend dev
        "http://localhost:8001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(outlets.router, prefix="/outlets", tags=["Outlets"])
app.include_router(food.router, prefix="/food", tags=["Food"])
app.include_router(drinks.router, prefix="/drinks", tags=["Drinks"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(embeddings.router, prefix="/embeddings", tags=["Embeddings"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

# ==============================
# Root endpoint
# ==============================
@app.get("/")
def root():
    return {"message": "ZUS Coffee Internal Assistant API is running"}
