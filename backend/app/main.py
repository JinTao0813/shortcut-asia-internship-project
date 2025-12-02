import os
import pickle
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss

from app.routers import products, outlets, chat
from dependencies import DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.faiss")
META_PATH = os.path.join(BASE_DIR, "data", "faiss_meta.pkl")

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
        ml_models["embed_model"] = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        print("SentenceTransformer loaded.")

        FAISS_INDEX_PATH = os.path.join("data", "faiss_index.faiss")
        META_PATH = os.path.join("data", "faiss_meta.pkl")

        if os.path.exists(FAISS_INDEX_PATH):
            ml_models["faiss_index"] = faiss.read_index(FAISS_INDEX_PATH)
            print("FAISS index loaded.")
        else:
            print(f"⚠️ FAISS index not found at {FAISS_INDEX_PATH}")

        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                ml_models["meta"] = pickle.load(f)
            print("Meta loaded.")
        else:
            print(f"⚠️ Meta file not found at {META_PATH}")

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
app = FastAPI(lifespan=lifespan)

# Attach the ml_models dict to app state
app.state.ml_models = ml_models

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "http://localhost:3000",  # alternative dev
        "https://mindhive-rag-assessment.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(outlets.router, prefix="/outlets", tags=["Outlets"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# ==============================
# Root endpoint
# ==============================
@app.get("/")
def root():
    return {"message": "ZUS Coffee Agent API is running"}
