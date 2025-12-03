import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_community.utilities import SQLDatabase

load_dotenv()

DATA_DIR = "data"
DRINKWARE_JSON = os.path.join(DATA_DIR, "drinkware.json")
OUTLETS_JSON = os.path.join(DATA_DIR, "outlets.json")

DATABASE_DIR = "database"
DATABASE_PATH = os.path.join(DATABASE_DIR, "zus_coffee_internal.db")

FAISS_INDEX_PATH = os.path.join(DATA_DIR, "zus_embeddings.index")
PKL_PATH = os.path.join(DATA_DIR, "zus_embeddings.pkl")
META_PATH = os.path.join(DATA_DIR, "faiss_meta.pkl")

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Fast and free-tier eligible
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

llm = get_llm()
